# Sandbox utilities

This folder contains small utilities used to start the project sandbox, run tests inside Docker, and analyze test logs with an LLM.

Files
- `manager.py` — helper that starts/stops the docker compose sandbox and collects logs (uses Docker CLI).
- `run_sandbox.py` — convenience script that uses `SandboxManager` to start the sandbox, run tests, and stop it.
- `llm_analyze.py` — collects test logs (or starts the sandbox to produce them), sends them to a Gemini model (if configured via env vars), and writes an analysis to `logs/analysis_result_<timestamp>.txt`.

Quick usage

Prerequisites:
- Python 3.8+
- requests (install with `pip install requests`)
- Docker + Docker Compose and npm (if you want to run the sandbox / test-runner)
- Optionally set a Gemini key/URL (GEMINI_API_KEY and/or GEMINI_API_URL in project `.env` or env)

From the project root (recommended):

Windows (cmd.exe)
```
python sandbox\llm_analyze.py
```
Or run just the sandbox/test sequence to produce logs (no LLM):
```
python sandbox\run_sandbox.py
```

Unix/macOS (bash / zsh)
```
python3 sandbox/llm_analyze.py
# or
python3 -m sandbox.llm_analyze
```

Notes and troubleshooting
- If `logs/` already contains .txt files, `llm_analyze.py` will use them instead of starting Docker. Remove or rename logs files to force a sandbox run.
- If Docker isn't available, the manager will raise an error; `llm_analyze.py` tries a local `npm test` fallback.
- The script reads `.env` at project root automatically (see `load_env()`), so adding your GEMINI_API_KEY to the root `.env` is the easiest way to enable remote LLM analysis.

Where results are saved
- Analysis files created by `llm_analyze.py` are written to `logs/analysis_result_<timestamp>.txt` (root `logs/`).

If you want, you can add a `.gitignore` entry to ignore the `logs/` directory and the `.env` file — this repo already includes those in the root `.gitignore`.

Happy debugging!
