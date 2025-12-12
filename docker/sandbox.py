#!/usr/bin/env python3
"""
sandbox.py

Python sandbox generator equivalent of generate-project.cjs.

Enhancement:
 - run_sandbox() accepts four JSON dict inputs:
        run_sandbox(frontend_json, backend_json, tests_json, docker_json)

 - If run directly OR if inputs are None:
        it falls back to reading frontend.json, backend.json, tests.json, docker-compose.json

Functionality preserved:
 - Writes project files to ./project/
 - Runs npm install
 - Runs docker compose up -d --build
 - Saves ALL logs in one JSON file
 - Opens frontend automatically
"""

import os
import sys
import json
import re
import subprocess
import time
import http.client
import webbrowser
from pathlib import Path

PROJECT_ROOT = Path.cwd() / "project"
LOG_ROOT = PROJECT_ROOT / "docker_logs"


# ------------------------------------------
# Helpers
# ------------------------------------------
def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def safe_exec(cmd, cwd=None):
    try:
        res = subprocess.run(
            cmd, cwd=cwd, shell=True,
            capture_output=True, text=True, encoding='utf-8', errors='replace'
        )
        return {
            "ok": res.returncode == 0,
            "stdout": res.stdout or "",
            "stderr": res.stderr or "",
            "code": res.returncode,
        }
    except Exception as e:
        return {"ok": False, "stdout": "", "stderr": str(e), "code": 1}

def write_utf8(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf8")


# ------------------------------------------
# JSON writing from dict
# ------------------------------------------
def write_json_dict(json_dict: dict):
    for rel_path, content in json_dict.items():
        full = PROJECT_ROOT / rel_path
        ensure_dir(full.parent)
        write_utf8(full, content)
        print(f"  [OK] Wrote {rel_path}")


# ------------------------------------------
# Load JSON files (fallback mode)
# ------------------------------------------
def load_json_file(filename):
    p = Path(filename)
    if not p.exists():
        print(f"[WARN] Missing {filename}, using empty JSON.")
        return {}
    try:
        return json.loads(p.read_text(encoding="utf8"))
    except Exception as e:
        print(f"[ERROR] JSON parse error in {filename}: {e}")
        return {}

def load_all_json_files():
    return (
        load_json_file("frontend.json"),
        load_json_file("backend.json"),
        load_json_file("tests.json"),
        load_json_file("docker-compose.json"),
    )


# ------------------------------------------
# npm install
# ------------------------------------------
def maybe_install_frontend():
    pkg = PROJECT_ROOT / "frontend" / "package.json"
    if not pkg.exists():
        print("\nNo frontend/package.json → skipping npm install.")
        return

    print("\nRunning npm install in frontend...")
    try:
        subprocess.run(
            "npm install --no-audit --no-fund",
            cwd=str(pkg.parent),
            shell=True,
            check=True
        )
        print("  [OK] npm install completed.")
    except Exception as e:
        print("  [WARN] npm install failed:", e)


# ------------------------------------------
# docker compose
# ------------------------------------------
def start_docker_compose():
    print("\nStarting Docker Compose (detached, build)...")
    res = safe_exec("docker compose up -d --build", cwd=str(PROJECT_ROOT))
    if not res["ok"]:
        print("[ERROR] docker compose failed:", res["stderr"])
    else:
        print("[OK] docker compose started.")


# ------------------------------------------
# Detect services & ports
# ------------------------------------------
def get_compose_text():
    f = PROJECT_ROOT / "docker-compose.yml"
    return f.read_text(encoding="utf8") if f.exists() else ""

def detect_services():
    text = get_compose_text()
    matches = re.finditer(r"^\s*([A-Za-z0-9_-]+):\s*$", text, re.MULTILINE)
    return [m.group(1) for m in matches if m.group(1) != "services"]

def detect_frontend_port():
    text = get_compose_text()
    if not text:
        return 3000

    # Extract ONLY the frontend service block
    svc_match = re.search(
        r"frontend:\s*([\s\S]*?)(?=^[A-Za-z0-9_-]+:|\Z)",
        text,
        re.MULTILINE
    )

    if not svc_match:
        return 3000  # fallback

    block = svc_match.group(1)

    # Look for ports: - "5173:5173"
    m = re.search(r'ports:\s*-\s*["\']?(\d+)\s*:', block)
    if m:
        return int(m.group(1))

    # More generic fallback inside frontend block
    m2 = re.search(r'["\']?(\d+)\s*:\s*["\']?\d+', block)
    if m2:
        return int(m2.group(1))

    return 3000  # fallback

# ------------------------------------------
# Save all logs
# ------------------------------------------
def save_all_logs_json():
    ensure_dir(LOG_ROOT)
    services = detect_services()
    logs = {}

    print("\nCollecting logs...")

    for svc in services:
        res = safe_exec(f"docker compose logs --no-color {svc}", cwd=str(PROJECT_ROOT))
        logs[svc] = res["stdout"] if res["ok"] else res["stderr"]
        print(f"  [OK] {svc}")

    ts = time.strftime("%Y-%m-%dT%H-%M-%S")
    out_file = LOG_ROOT / f"all_logs_{ts}.json"
    out_file.write_text(json.dumps(logs, indent=2), encoding="utf8")

    print("[OK] Logs saved:", out_file)
    return out_file


# ------------------------------------------
# wait for frontend
# ------------------------------------------
def wait_for_frontend(port, timeout_ms=180000):
    print(f"\nWaiting for frontend at http://localhost:{port}")
    deadline = time.time() + timeout_ms / 1000

    while time.time() < deadline:
        try:
            conn = http.client.HTTPConnection("localhost", port, timeout=2)
            conn.request("GET", "/")
            resp = conn.getresponse()
            resp.read()
            return True
        except Exception:
            time.sleep(1)

    return False

def open_browser_for(url):
    print("Opening browser:", url)
    try:
        webbrowser.open(url)
    except:
        pass


# ------------------------------------------
# CORE WORKFLOW
# ------------------------------------------
def sandbox_workflow(frontend_json, backend_json, tests_json, docker_json):
    print("=== Sandbox Generator ===")
    ensure_dir(PROJECT_ROOT)

    output = {
        "status": "success",
        "project_root": str(PROJECT_ROOT),
        "files_written": 0,
        "frontend_url": None,
        "logs_file": None,
        "errors": []
    }

    try:
        print("\n[*] Writing frontend files...")
        write_json_dict(frontend_json)
        output["files_written"] += 1

        print("\n[*] Writing backend files...")
        write_json_dict(backend_json)
        output["files_written"] += 1

        print("\n[*] Writing tests files...")
        write_json_dict(tests_json)
        output["files_written"] += 1

        print("\n[*] Writing docker files...")
        write_json_dict(docker_json)
        output["files_written"] += 1

        maybe_install_frontend()
        start_docker_compose()

        print("Waiting 3s for containers...")
        time.sleep(3)

        logs_file = save_all_logs_json()
        output["logs_file"] = str(logs_file)

        port = detect_frontend_port()
        url = f"http://localhost:{port}"
        output["frontend_url"] = url

        if wait_for_frontend(port):
            print("[OK] Frontend is ready:", url)
        else:
            print("[WARN] Frontend not responding yet, but opening browser anyway.")

        open_browser_for(url)

        print("\nDone.")
    except Exception as e:
        output["status"] = "error"
        output["errors"].append(str(e))
        print(f"[ERROR] Workflow failed: {e}")

    return output

# ------------------------------------------
# Public API
# ------------------------------------------
def run_sandbox(frontend_json, backend_json, tests_json, docker_json):
    """
    Programmatic API.
    ALL FOUR JSON OBJECTS ARE REQUIRED.
    """
    return sandbox_workflow(frontend_json, backend_json, tests_json, docker_json)


# ------------------------------------------
# CLI fallback (reads files)
# ------------------------------------------
if __name__ == "__main__":
    front, back, tests, dock = load_all_json_files()
    sandbox_workflow(front, back, tests, dock)
