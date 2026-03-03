"""Shared utilities for kaggle-notebook-deploy."""

import json
import re
import subprocess
import tempfile
from pathlib import Path


def normalize_path(path_str: str) -> str:
    """Convert Git Bash-style paths (/c/Users/...) to Windows paths (C:/Users/...).

    Git Bash on Windows converts paths to /c/Users/... format, which Python
    does not understand. This function detects and converts them.
    """
    if len(path_str) >= 3 and path_str[0] == '/' and path_str[1].isalpha() and path_str[2] == '/':
        return path_str[1].upper() + ':' + path_str[2:]
    return path_str


def get_kernel_status(kaggle_cmd: str, kernel_id: str) -> str:
    """Run kaggle kernels status and return the status string."""
    result = subprocess.run(
        [kaggle_cmd, "kernels", "status", kernel_id],
        capture_output=True,
        text=True,
    )
    raw = result.stdout + result.stderr
    m = re.search(r'has status "([^"]+)"', raw)
    return m.group(1) if m else ""


def show_kernel_diagnostics(kaggle_cmd: str, kernel_id: str) -> None:
    """Download kernel output and print stdout + last 30 stderr lines."""
    slug = kernel_id.split("/")[-1]
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run(
            [kaggle_cmd, "kernels", "output", kernel_id, "-p", tmpdir],
            capture_output=True,
        )
        log_file = Path(tmpdir) / f"{slug}.log"
        if not log_file.exists():
            print("(no kernel log found)")
            return

        entries = json.loads(log_file.read_text())

        stdout_lines = [e["data"] for e in entries if e.get("stream_name") == "stdout"]
        if stdout_lines:
            print("--- kernel stdout ---")
            print("".join(stdout_lines), end="")

        stderr_lines = [e["data"] for e in entries if e.get("stream_name") == "stderr"]
        if stderr_lines:
            print("\n--- last 30 stderr lines ---")
            print("".join(stderr_lines[-30:]), end="")
