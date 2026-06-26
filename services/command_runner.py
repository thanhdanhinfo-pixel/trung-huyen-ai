from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import Any

DENIED_TOKENS = {
    "rm", "sudo", "curl", "wget", "docker", "apt", "apt-get",
    "chmod", "chown", "mkfs", "dd", "shutdown", "reboot",
}

ALLOWED_PREFIXES = (
    ("python",),
    ("python3",),
    ("pytest",),
    ("git", "status"),
    ("git", "add"),
    ("git", "commit"),
)


def _is_allowed(parts: list[str]) -> bool:
    if not parts:
        return False
    if any(token in DENIED_TOKENS for token in parts):
        return False
    return any(tuple(parts[:len(prefix)]) == prefix for prefix in ALLOWED_PREFIXES)


def run_command(command: str, cwd: str | None = None, timeout: int = 60) -> dict[str, Any]:
    parts = shlex.split(command)
    if not _is_allowed(parts):
        return {
            "status": "error",
            "error_type": "CommandNotAllowed",
            "message": "Command is not allowed by whitelist policy.",
            "command": command,
        }

    workdir = Path(cwd or ".").resolve()
    completed = subprocess.run(
        parts,
        cwd=str(workdir),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return {
        "status": "ok" if completed.returncode == 0 else "error",
        "command": command,
        "cwd": str(workdir),
        "returncode": completed.returncode,
        "stdout": completed.stdout[-12000:],
        "stderr": completed.stderr[-12000:],
    }
