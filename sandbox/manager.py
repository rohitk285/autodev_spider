import subprocess
try:
    import docker
except Exception:
    # importing docker SDK may succeed but creating a client can fail
    docker = None
import time
from datetime import datetime

client = None

def _docker_cli_available():
    try:
        res = subprocess.run(["docker", "info"], capture_output=True)
        if res.returncode == 0:
            return True, None
        # non-zero return code — return stderr if present
        stderr = res.stderr.decode("utf-8", errors="replace") if res.stderr else ""
        return False, stderr or "docker info returned non-zero exit code"
    except FileNotFoundError:
        return False, "docker executable not found. Is Docker installed?"
    except Exception as e:
        return False, str(e)

class SandboxManager:

    def __init__(self, project_name="mern_sandbox"):
        self.project_name = project_name

    def start_sandbox(self):
        print("Starting sandbox using docker compose...")

        ok, msg = _docker_cli_available()
        if not ok:
            print("Docker does not appear to be available or running on this machine:")
            print("  ", msg)
            print("Please start Docker Desktop (Windows) / Docker daemon, or make sure the 'docker' CLI is in your PATH.")
            raise RuntimeError("Docker not available — sandbox cannot be started")

        # If the host already has a listener on Mongo's default port, the
        # compose job will fail trying to bind 27017. Detect that and use a
        # sandbox-specific compose override (docker-compose.sandbox.yml)
        # which prevents mapping mongo's host port.
        use_override = False
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            # attempt to connect to localhost:27017 — if successful, port is in use
            if sock.connect_ex(("127.0.0.1", 27017)) == 0:
                use_override = True
            sock.close()
        except Exception:
            # if detection fails, fall back to default behavior and let docker
            # report any errors
            use_override = False

        try:
            # Run the initial compose command, capturing stdout/stderr so we can
            # inspect errors programmatically (particularly port bind problems).
            if use_override:
                print("Detected port 27017 already in use on host — starting sandbox without publishing Mongo host port.")
                cmd = [
                    "docker", "compose", "-p", self.project_name,
                    "-f", "docker-compose.yml", "-f", "docker-compose.sandbox.yml",
                    "up", "-d", "--build"
                ]
            else:
                cmd = ["docker", "compose", "-p", self.project_name, "up", "-d", "--build"]

            res = subprocess.run(cmd, capture_output=True)
            if res.returncode != 0:
                stderr_text = (res.stderr.decode("utf-8", errors="replace") if res.stderr else "")
                stdout_text = (res.stdout.decode("utf-8", errors="replace") if res.stdout else "")
                print("Failed to start sandbox with docker-compose. stdout/stderr below:\n", stdout_text, stderr_text)
                # fall through to the exception handler below which will examine
                # stderr_text and attempt an alternate override if necessary
                e = subprocess.CalledProcessError(res.returncode, cmd)
                e.stderr = stderr_text
                e.stdout = stdout_text
                raise e
        except subprocess.CalledProcessError as e:
            # Provide a friendly, actionable message for port allocation errors
            print("Failed to start sandbox with docker-compose.")
            stderr = getattr(e, 'stderr', None)
            # exception may carry bytes or string
            if isinstance(stderr, bytes):
                stderr_text = stderr.decode("utf-8", errors="replace")
            else:
                stderr_text = str(stderr or "")
            # If the sandbox override still triggered a host-port bind error
            # we try a second override that maps mongo to a non-default host
            # port (27018). This makes the sandbox more resilient when the
            # developer already runs Mongo locally.
            if stderr_text and ("Bind for" in stderr_text or "port is already allocated" in stderr_text or "address already in use" in stderr_text):
                print("Bind error detected when starting sandbox; trying alternate override with host port 27018...")
                try:
                    alt_cmd = [
                        "docker", "compose", "-p", self.project_name,
                        "-f", "docker-compose.yml", "-f", "docker-compose.sandbox.alt.yml",
                        "up", "-d", "--build",
                    ]
                    alt_res = subprocess.run(alt_cmd, capture_output=True)
                    if alt_res.returncode != 0:
                        print("Alternate compose attempt stderr:\n", alt_res.stderr.decode("utf-8", errors="replace"))
                        raise subprocess.CalledProcessError(alt_res.returncode, alt_cmd)
                except subprocess.CalledProcessError:
                    print("Alternate fallback compose also failed. See docker output above for details.")
                    raise
                else:
                    print("Sandbox started with alternate host port mapping (mongo -> 27018).")
                    return
            if stderr and "Bind for" in stderr_text:
                print("It looks like port 27017 is already in use. You can:")
                print("  • Stop the process using that port (on Windows: `netstat -ano | findstr :27017` then `taskkill /PID <pid> /F`) or")
                print("  • Run the sandbox without publishing Mongo's port (the manager will do that automatically).")
            raise

        print("Sandbox started successfully.")

    def run_tests(self):
        print("Running test container...")
        ok, msg = _docker_cli_available()
        if not ok:
            print("Docker CLI is not available or cannot reach the daemon:")
            print("  ", msg)
            raise RuntimeError("Docker not available — cannot run tests in sandbox")

        # Run test-runner as ephemeral container. Capture raw bytes so we can
        # decode safely (avoid UnicodeDecodeError when output contains bytes
        # that don't map to the host encoding).
        result = subprocess.run(
            ["docker", "compose", "-p", self.project_name, "run", "--rm", "test-runner"],
            capture_output=True
        )

        def _safe_decode(b):
            if not b:
                return ""
            if isinstance(b, bytes):
                try:
                    return b.decode("utf-8")
                except Exception:
                    return b.decode("utf-8", errors="replace")
            return str(b)

        stdout = _safe_decode(result.stdout)
        stderr = _safe_decode(result.stderr)

        logs = stdout + "\n" + stderr

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        import os
        os.makedirs("logs", exist_ok=True)

        # Save the immediate test-runner output to its own file (this captures
        # the test output even when docker removes the ephemeral container).
        test_log_file = f"logs/test-runner_{timestamp}.txt"
        with open(test_log_file, "w", encoding="utf-8") as f:
            f.write(logs)

        # Also collect per-service compose logs for persistent containers
        # (mongo, server, client) using `docker compose logs` so we have
        # additional context when debugging failures.
        services_to_collect = ["mongo", "server", "client"]
        compose_prefix = ["docker", "compose", "-p", self.project_name, "logs", "--no-color"]

        collected = {"test-runner": test_log_file}

        for service in services_to_collect:
            cmd = compose_prefix + [service]
            try:
                svc_res = subprocess.run(cmd, capture_output=True)
            except Exception as e:
                svc_stdout = b""
                svc_stderr = str(e).encode("utf-8")
            else:
                svc_stdout = svc_res.stdout or b""
                svc_stderr = svc_res.stderr or b""

            svc_out = _safe_decode(svc_stdout)
            svc_err = _safe_decode(svc_stderr)
            svc_logs = svc_out + "\n" + svc_err

            svc_file = f"logs/{service}_logs_{timestamp}.txt"
            with open(svc_file, "w", encoding="utf-8") as f:
                f.write(svc_logs)

            collected[service] = svc_file

        # Save combined compose logs too (all services)
        try:
            all_res = subprocess.run(["docker", "compose", "-p", self.project_name, "logs", "--no-color"], capture_output=True)
            all_out = _safe_decode(all_res.stdout or b"")
            all_err = _safe_decode(all_res.stderr or b"")
            combined = all_out + "\n" + all_err
        except Exception as e:
            combined = f"Failed to collect combined logs: {e}"

        combined_file = f"logs/compose_logs_{timestamp}.txt"
        with open(combined_file, "w", encoding="utf-8") as f:
            f.write(combined)

        collected["compose"] = combined_file

        print(f"Test logs saved to {test_log_file}")
        print("Saved service logs:")
        for name, path in collected.items():
            print(f"  - {name}: {path}")

        # return dict with file paths so callers can inspect
        return collected

    def stop_sandbox(self):
        print("Stopping sandbox containers...")
        ok, msg = _docker_cli_available()
        if not ok:
            print("Docker CLI not available when attempting to stop sandbox:")
            print("  ", msg)
            raise RuntimeError("Docker not available — cannot stop sandbox containers")

        subprocess.run(
            ["docker", "compose", "-p", self.project_name, "down"],
            check=True
        )
        print("Sandbox stopped.")
