import importlib
import importlib.util
from pathlib import Path
import sys


def get_sandbox_manager_class():
    try:
        # Normal import when run from project root
        from sandbox.manager import SandboxManager

        return SandboxManager
    except Exception:
        # Fallback: load module from file path when the script is executed
        # directly (e.g. `python sandbox/run_sandbox.py`) — in that case
        # sys.path[0] is sandbox/ and 'import sandbox' doesn't work.
        mgr_path = Path(__file__).resolve().parents[1] / "sandbox" / "manager.py"
        if not mgr_path.exists():
            raise
        spec = importlib.util.spec_from_file_location("sandbox.manager", str(mgr_path))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return getattr(mod, "SandboxManager")


if __name__ == "__main__":
    SandboxManager = get_sandbox_manager_class()
    sb = SandboxManager("mern-sandbox")

    sb.start_sandbox()

    logs = sb.run_tests()
    print("==== TEST OUTPUT ====")
    print(logs)

    sb.stop_sandbox()
