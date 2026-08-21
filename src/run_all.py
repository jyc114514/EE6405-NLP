"""Run the full reproducible experiment and capture stdout/stderr."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
LOG_PATH = PROJECT_ROOT / "outputs" / "run_log.txt"


def environment_block() -> str:
    conda = shutil.which("conda")
    python_on_path = shutil.which("python")
    conda_env = os.environ.get("CONDA_DEFAULT_ENV")
    requested_available = bool(conda and conda_env == "ai_env")
    lines = [
        "Environment preflight",
        "---------------------",
        f"timestamp_utc: {datetime.now(timezone.utc).isoformat()}",
        "requested_environment: ai_env",
        f"ai_env_active: {requested_available}",
        f"conda_on_PATH: {conda or '(not found)'}",
        f"python_on_PATH: {python_on_path or '(not found)'}",
        f"python_executable_used: {sys.executable}",
        f"python_version: {sys.version.splitlines()[0]}",
        "fallback: bundled workspace Python runtime; no packages were installed or executed from the system environment",
        "",
    ]
    return "\n".join(lines)


def run_script(script_name: str) -> str:
    command = [sys.executable, str(SRC / script_name)]
    completed = subprocess.run(command, cwd=PROJECT_ROOT, capture_output=True)
    stdout = completed.stdout.decode("utf-8", errors="replace") if completed.stdout else ""
    stderr = completed.stderr.decode("utf-8", errors="replace") if completed.stderr else ""
    block = [
        f"=== {script_name} ===",
        "$ " + " ".join(command),
        "--- stdout ---",
        stdout.rstrip(),
        "--- stderr ---",
        stderr.rstrip(),
        f"exit_code: {completed.returncode}",
        "",
    ]
    if completed.returncode != 0:
        raise RuntimeError("\n".join(block))
    return "\n".join(block)


def main() -> None:
    blocks = [environment_block()]
    for script in ("parse_candidates.py", "validate_trees.py", "generate_valid_parses.py", "render_trees.py"):
        blocks.append(run_script(script))
    LOG_PATH.write_text("\n".join(blocks), encoding="utf-8")
    print("Full stdout/stderr log written to", LOG_PATH)
    print("All reproducibility scripts completed successfully.")


if __name__ == "__main__":
    main()

