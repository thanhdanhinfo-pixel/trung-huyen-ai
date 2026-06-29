"""Safe shell execution service for TRUNG_HUYEN_AI_OS.

This service exposes a narrow allowlist of infrastructure commands so the
runtime can trigger deployment and diagnostics without granting arbitrary shell
access.
"""

from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List


ALLOWED_PREFIXES: List[List[str]] = [
    ["gcloud", "builds", "submit"],
    ["pytest"],
    ["python", "scripts"],
    ["docker", "build"],
    ["docker", "push"],
]

DEFAULT_TIMEOUT_SECONDS = 900
MAX_OUTPUT_CHARS = 20000


def _is_allowed(parts: List[str]) -> bool:
    if not parts:
        return False

    for prefix in ALLOWED_PREFIXES:
        if len(parts) >= len(prefix) and parts[: len(prefix)] == prefix:
            return True
    return False


def shell_exec(command: str, cwd: str = ".", timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> Dict[str, Any]:
    """Execute an allowlisted shell command and return structured output."""

    if not command or not command.strip():
        return {"status": "error", "message": "command is required"}

    try:
        parts = shlex.split(command)
    except ValueError as exc:
        return {"status": "error", "message": f"invalid command: {exc}"}

    if not _is_allowed(parts):
        return {
            "status": "error",
            "message": "command is not allowlisted",
            "allowed_prefixes": [" ".join(prefix) for prefix in ALLOWED_PREFIXES],
        }

    workdir = Path(cwd or ".").resolve()
    timeout = max(1, min(int(timeout_seconds or DEFAULT_TIMEOUT_SECONDS), DEFAULT_TIMEOUT_SECONDS))

    try:
        completed = subprocess.run(
            parts,
            cwd=str(workdir),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        return {"status": "error", "message": f"executable not found: {exc}"}
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "error",
            "message": "command timed out",
            "timeout_seconds": timeout,
            "stdout": (exc.stdout or "")[:MAX_OUTPUT_CHARS],
            "stderr": (exc.stderr or "")[:MAX_OUTPUT_CHARS],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc), "error_type": type(exc).__name__}

    return {
        "status": "ok" if completed.returncode == 0 else "error",
        "returncode": completed.returncode,
        "command": command,
        "cwd": str(workdir),
        "stdout": (completed.stdout or "")[:MAX_OUTPUT_CHARS],
        "stderr": (completed.stderr or "")[:MAX_OUTPUT_CHARS],
    }


def trigger_cloud_build(config: str = "cloudbuild.yaml", cwd: str = ".") -> Dict[str, Any]:
    """Trigger Google Cloud Build using the repository cloudbuild config."""

    command = f"gcloud builds submit --config {shlex.quote(config)}"
    return shell_exec(command=command, cwd=cwd, timeout_seconds=DEFAULT_TIMEOUT_SECONDS)
