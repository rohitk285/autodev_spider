#!/usr/bin/env python3
"""
Run sandbox → collect test logs → send to Gemini → save analysis.
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

# ----------------------------
# Paths & ENV
# ----------------------------
ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
ENV_FILE = ROOT / ".env"

def load_env():
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or "=" not in line or line.startswith("#"):
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ----------------------------
# Utilities
# ----------------------------
def now_ts():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def safe_read(path: Path, max_chars=20000):
    try:
        data = path.read_text(errors="replace")
        if len(data) > max_chars:
            return data[:max_chars//2] + "\n...\n" + data[-max_chars//2:]
        return data
    except Exception as e:
        return f"<error reading {path}: {e}>"

# ----------------------------
# 1. RUN SANDBOX TESTS
# ----------------------------

def run_sandbox_tests():
    """
    Returns dict: {filename -> file_path}
    """
    # Import gracefully: when running this file directly (python sandbox/llm_analyze.py)
    # sys.path[0] becomes the sandbox/ directory which prevents 'import sandbox' to
    # find the package. Try the package import first, then fall back to loading
    # manager.py by file path.
    SandboxManager = None
    try:
        from sandbox.manager import SandboxManager as _SM
        SandboxManager = _SM
    except Exception:
        # fallback: load by path
        mgr_path = ROOT / "sandbox" / "manager.py"
        if mgr_path.exists():
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("sandbox.manager", str(mgr_path))
                mod = importlib.util.module_from_spec(spec)
                loader = spec.loader
                if loader:
                    loader.exec_module(mod)
                    SandboxManager = getattr(mod, "SandboxManager", None)
            except Exception as e:
                print("[sandbox] Failed to import SandboxManager from path:", e)

    if SandboxManager is None:
        print("[sandbox] Could not import SandboxManager: not available in environment or file system")
        return None

    mgr = SandboxManager("mern-sandbox")

    try:
        mgr.start_sandbox()
        results = mgr.run_tests()   # returns dict
    except Exception as e:
        print("[sandbox] Test execution failed:", e)
        return None
    finally:
        try:
            mgr.stop_sandbox()
        except:
            pass

    return results

# ----------------------------
# 2. LOCAL fallback
# ----------------------------
def run_local_tests():
    LOG_DIR.mkdir(exist_ok=True, parents=True)
    ts = now_ts()
    outfile = LOG_DIR / f"local_test_{ts}.txt"

    try:
        p = subprocess.run(["npm", "test"], capture_output=True)
    except FileNotFoundError:
        return None

    text = p.stdout.decode("utf-8", "replace") + "\n--- STDERR ---\n" + p.stderr.decode()
    outfile.write_text(text)
    return str(outfile)

# ----------------------------
# Build prompt
# ----------------------------
def build_prompt(logs):
    header = (
        "You are a senior engineer. Analyze the logs.\n"
        "If all tests passed, return ONLY:\n"
        "ALL_TESTS_PASSED\nReady to export.\n\n"
        "If tests failed, return a short agent-ready remediation plan.\n\n"
    )
    body = "\n\n".join([f"### {name}\n{content}" for name, content in logs.items()])
    return header + body

# ----------------------------
# Gemini call
# ----------------------------
def call_gemini(prompt: str):
    # Don't include API keys or secrets in logs — just indicate whether
    # they were present. Prefer GEMINI_API_URL if set; otherwise construct a
    # reasonable default endpoint for Google Generative API using the key.
    if not GEMINI_API_KEY and not os.getenv("GEMINI_API_URL"):
        return None, "missing GEMINI_API_KEY and GEMINI_API_URL"

    try:
        import requests
    except Exception:
        return None, "requests library not installed"

    url = os.getenv("GEMINI_API_URL")
    if not url:
        # fallback: build Google GL API endpoint with key param
        url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            "models/gemini-2.5-pro:generateContent?key=" + GEMINI_API_KEY
        )

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        res = requests.post(url, json=payload, timeout=60)
    except Exception as e:
        return None, f"network request failed: {e}"

    status = getattr(res, "status_code", None)
    text = None
    try:
        text = res.text
    except Exception:
        text = None

    # Non-2xx responses should return a clear error describing status and a
    # short excerpt of the body to help debugging (truncate to avoid huge files).
    if status is None or not (200 <= status < 300):
        body_excerpt = (text[:1000] + "..." ) if text and len(text) > 1000 else (text or "<no body>")
        return None, f"HTTP {status} - {body_excerpt}"

    try:
        body = res.json()
    except Exception:
        # If response isn't JSON, return full text
        return text, None

    # Try to handle various shapes and return the most likely content
    # (Google GL might return 'candidates' where content.parts[].text lives)
    if isinstance(body, dict):
        if "candidates" in body and isinstance(body["candidates"], list) and body["candidates"]:
            c = body["candidates"][0]
            try:
                return c["content"]["parts"][0]["text"], None
            except Exception:
                pass

        # Some endpoints use 'outputs' or other nested forms — search for a string
        def find_text(obj):
            if isinstance(obj, str):
                return obj
            if isinstance(obj, list):
                for i in obj:
                    t = find_text(i)
                    if t:
                        return t
            if isinstance(obj, dict):
                for v in obj.values():
                    t = find_text(v)
                    if t:
                        return t
            return None

        found = find_text(body)
        if found:
            return found, None

    return json.dumps(body, indent=2) if body is not None else text, None

# ----------------------------
# Local fallback analysis
# ----------------------------
def local_analysis(logs):
    combined = "\n".join(logs.values()).lower()

    if "fail" not in combined:
        return "ALL_TESTS_PASSED\nReady to export."

    return (
        "Tests failed. Provide a remediation plan: list failing tests, "
        "likely causes, and file-level fixes.\n\n"
        "Summary of logs:\n" + combined[:2000]
    )


def collect_existing_logs(limit_files: int = 20, max_chars: int = 20000) -> dict:
    """Collect text files from logs/ (most recent first) and return as {name: content}.

    Truncates large files to keep prompt sizes reasonable.
    """
    if not LOG_DIR.exists():
        return {}
    files = sorted(LOG_DIR.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
    out = {}
    for p in files[:limit_files]:
        try:
            raw = p.read_text(encoding="utf-8", errors="replace")
            if len(raw) > max_chars:
                head = raw[: int(max_chars / 2)]
                tail = raw[-int(max_chars / 2) :]
                raw = f"[truncated head]\n{head}\n...\n[truncated tail]\n{tail}"
            out[p.name] = raw
        except Exception as e:
            out[p.name] = f"<error reading {p}: {e}>"

    return out

# ----------------------------
# MAIN
# ----------------------------
def main():
    print("=== Running sandbox tests ===")

    logs = {}

    # If logs folder already contains files, prefer those rather than starting
    # a sandbox run. This speeds up iterative use and avoids long Docker startup
    # when you already produced logs.
    if LOG_DIR.exists() and any(LOG_DIR.glob("*.txt")):
        print("Found existing logs in logs/ — using those instead of starting the sandbox")
        logs = collect_existing_logs()
    else:
        # 1. Try sandbox
        results = run_sandbox_tests()
    if results:
        for name, path in results.items():
            logs[name] = safe_read(Path(path))

    # 2. Fallback to local npm test
    if not logs:
        local = run_local_tests()
        if local:
            logs[Path(local).name] = safe_read(Path(local))

    if not logs:
        print("No logs available.")
        return 1

    # Build prompt
    prompt = build_prompt(logs)

    # Try Gemini
    print("=== Running LLM Analysis ===")

    response, err = call_gemini(prompt)

    # Diagnostic header so analyzer files contain clear context about whether
    # the remote call was attempted and why it might have failed. Avoid writing
    # sensitive secrets (keys) into the file — only indicate presence.
    diag = []
    diag.append("=== Analyzer diagnostics ===")
    diag.append(f"GEMINI_API_KEY present: {'yes' if bool(os.getenv('GEMINI_API_KEY')) else 'no'}")
    diag.append(f"GEMINI_API_URL present: {'yes' if bool(os.getenv('GEMINI_API_URL')) else 'no'}")

    if response:
        output = response
        diag.append("Remote model call succeeded.")
    else:
        diag.append(f"Remote model call failed: {err}")
        diag.append("Falling back to local heuristic analysis.")
        output = local_analysis(logs)

    # Prepend diagnostics to output stored in the result file for visibility.
    response = "\n".join(diag) + "\n\n" + (output or "<no analysis produced>")

    # Save analysis
    LOG_DIR.mkdir(exist_ok=True, parents=True)
    outfile = LOG_DIR / f"analysis_result_{now_ts()}.txt"
    outfile.write_text(response)
    print("Saved analysis to:", outfile)

    return 0

if __name__ == "__main__":
    exit(main())
