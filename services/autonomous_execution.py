"""Autonomous Execution V1 for TRUNG_HUYEN_AI_OS. 

Provides strictly allowlisted runtime execution helpers for git sync,
Cloud Build, and Cloud Run deploy. These helpers are registered through
services.action_registry and are intended to be called only after Founder
approval/unified unlock according to governance.
"""

from __future__ import annotations

import os
import shlex
import subprocess
from typing import Any, Dict, Iterable

import google.auth
from googleapiclient.discovery import build

DEFAULT_TIMEOUT_SECONDS = int(os.getenv("AUTONOMOUS_EXEC_TIMEOUT_SECONDS", "900"))

ALLOWED_COMMAND_PREFIXES = (
    "git status",
    "git log",
    "git pull",
    "git fetch",
    "gcloud builds submit",
    "gcloud run deploy",
    "gcloud run services describe",
    "gcloud artifacts repositories list",
    "curl ",
    "python -m pytest",
)

DEFAULT_IMAGE = "asia-southeast1-docker.pkg.dev/trung-huyen-ai/thos/trung-huyen-ai"
DEFAULT_SERVICE = "trung-huyen-ai"
DEFAULT_REGION = "asia-southeast1"


def _normalize(command: str) -> str:
    return " ".join((command or "").strip().split())


def _tail(text: str, limit: int = 12000) -> str:
    return (text or "")[-limit:]


def allowed_prefixes() -> Iterable[str]:
    return ALLOWED_COMMAND_PREFIXES


def is_command_allowed(command: str) -> bool:
    normalized = _normalize(command)
    return any(normalized.startswith(prefix) for prefix in ALLOWED_COMMAND_PREFIXES)


def shell_exec(command: str, timeout: int | None = None, cwd: str | None = None) -> Dict[str, Any]:
    """Execute an allowlisted shell command and return structured output."""
    normalized = _normalize(command)
    if not normalized:
        return {"status": "error", "message": "command is required"}

    if not is_command_allowed(normalized):
        return {
            "status": "error",
            "message": "command is not allowlisted",
            "command": normalized,
            "allowed_prefixes": list(ALLOWED_COMMAND_PREFIXES),
        }

    try:
        completed = subprocess.run(
            normalized,
            shell=True,
            cwd=cwd or os.getcwd(),
            capture_output=True,
            text=True,
            timeout=timeout or DEFAULT_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "error",
            "message": "command timed out",
            "command": normalized,
            "timeout": timeout or DEFAULT_TIMEOUT_SECONDS,
            "stdout": _tail(exc.stdout if isinstance(exc.stdout, str) else ""),
            "stderr": _tail(exc.stderr if isinstance(exc.stderr, str) else ""),
        }

    return {
        "status": "ok" if completed.returncode == 0 else "error",
        "command": normalized,
        "returncode": completed.returncode,
        "stdout": _tail(completed.stdout),
        "stderr": _tail(completed.stderr),
    }


def git_pull(remote: str = "origin", branch: str = "main") -> Dict[str, Any]:
    remote_q = shlex.quote(remote or "origin")
    branch_q = shlex.quote(branch or "main")
    return shell_exec(f"git pull --rebase {remote_q} {branch_q}")


def _google_project_id(explicit_project_id: str | None = None) -> str:
    if explicit_project_id:
        return explicit_project_id
    env_project = (
        os.getenv("GOOGLE_CLOUD_PROJECT")
        or os.getenv("GCP_PROJECT")
        or os.getenv("PROJECT_ID")
    )
    if env_project:
        return env_project
    _, detected_project = google.auth.default()
    if not detected_project:
        raise RuntimeError("Unable to determine Google Cloud project id")
    return detected_project


def cloud_build_submit(
    tag: str = DEFAULT_IMAGE,
    project_id: str | None = None,
    repo_url: str = "https://github.com/thanhdanhinfo-pixel/trung-huyen-ai",
    revision: str = "main",
    service: str = DEFAULT_SERVICE,
    region: str = DEFAULT_REGION,
) -> Dict[str, Any]:
    """Trigger Cloud Build through Cloud Build API instead of requiring gcloud CLI."""
    try:
        project = _google_project_id(project_id)
        image = tag or DEFAULT_IMAGE
        cloudbuild = build("cloudbuild", "v1", cache_discovery=False)
        build_body = {
            "source": {
                "gitSource": {
                    "url": repo_url,
                    "revision": revision or "main",
                }
            },
            "steps": [
                {
                    "name": "gcr.io/cloud-builders/docker",
                    "args": ["build", "-t", image, "."],
                },
                {
                    "name": "gcr.io/cloud-builders/docker",
                    "args": ["push", image],
                },
                {
                    "name": "gcr.io/google.com/cloudsdktool/cloud-sdk",
                    "entrypoint": "gcloud",
                    "args": [
                        "run",
                        "deploy",
                        service or DEFAULT_SERVICE,
                        "--image",
                        image,
                        "--region",
                        region or DEFAULT_REGION,
                        "--platform",
                        "managed",
                        "--allow-unauthenticated",
                    ],
                },
            ],
            "images": [image],
        }
        operation = cloudbuild.projects().builds().create(
            projectId=project,
            body=build_body,
        ).execute()
        metadata = operation.get("metadata", {}) if isinstance(operation, dict) else {}
        build_info = metadata.get("build", {}) if isinstance(metadata, dict) else {}
        return {
            "status": "ok",
            "provider": "cloud_build_api",
            "project_id": project,
            "image": image,
            "service": service,
            "region": region,
            "operation": operation,
            "build_id": build_info.get("id"),
            "log_url": build_info.get("logUrl"),
        }
    except Exception as exc:
        return {
            "status": "error",
            "provider": "cloud_build_api",
            "message": str(exc),
            "type": type(exc).__name__,
        }


def cloud_run_deploy(
    service: str = DEFAULT_SERVICE,
    image: str = DEFAULT_IMAGE,
    region: str = DEFAULT_REGION,
    allow_unauthenticated: bool = True,
) -> Dict[str, Any]:
    service_q = shlex.quote(service or DEFAULT_SERVICE)
    image_q = shlex.quote(image or DEFAULT_IMAGE)
    region_q = shlex.quote(region or DEFAULT_REGION)
    command = f"gcloud run deploy {service_q} --image {image_q} --region {region_q}"
    if allow_unauthenticated:
        command += " --allow-unauthenticated"
    return shell_exec(command, timeout=1800)
