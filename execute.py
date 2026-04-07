import importlib.util
import subprocess
import sys

AGENT_PYTHON = "/opt/venv/bin/python"


def ensure_package(module_name: str, package_name: str | None = None) -> int:
    if importlib.util.find_spec(module_name) is not None:
        return 0
    pkg = package_name or module_name
    return subprocess.call([AGENT_PYTHON, "-m", "pip", "install", pkg])


def main() -> int:
    return ensure_package("requests")


if __name__ == "__main__":
    sys.exit(main())
