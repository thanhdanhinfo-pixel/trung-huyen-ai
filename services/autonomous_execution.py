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


def cloud_build_status(build_id: str, project_id: str | None = None) -> Dict[str, Any]:
    """Return Cloud Build status through the Cloud Build API."""
    if not build_id:
        return {"status": "error", "message": "build_id is required"}
    try:
        project = _google_project_id(project_id)
        cloudbuild = build("cloudbuild", "v1", cache_discovery=False)
        build_info = cloudbuild.projects().builds().get(
            projectId=project,
            id=build_id,
        ).execute()
        return {
            "status": "ok",
            "project_id": project,
            "build_id": build_id,
            "build_status": build_info.get("status"),
            "log_url": build_info.get("logUrl"),
            "create_time": build_info.get("createTime"),
            "start_time": build_info.get("startTime"),
            "finish_time": build_info.get("finishTime"),
            "substitutions": build_info.get("substitutions", {}),
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "type": type(exc).__name__,
            "build_id": build_id,
        }


def cloud_run_service_status(
    service: str = DEFAULT_SERVICE,
    region: str = DEFAULT_REGION,
) -> Dict[str, Any]:
    """Return Cloud Run service status through allowlisted gcloud describe."""
    service_q = shlex.quote(service or DEFAULT_SERVICE)
    region_q = shlex.quote(region or DEFAULT_REGION)
    command = f"gcloud run services describe {service_q} --region={region_q} --format=json"
    result = shell_exec(command, timeout=120)
    result["service"] = service or DEFAULT_SERVICE
    result["region"] = region or DEFAULT_REGION
    return result


def runtime_logs(
    service: str = DEFAULT_SERVICE,
    limit: int = 50,
    project_id: str | None = None,
) -> Dict[str, Any]:
    """Return recent Cloud Run logs through google-cloud-logging client."""
    try:
        import google.cloud.logging

        project = _google_project_id(project_id)
        client = google.cloud.logging.Client(project=project)
        limit = max(1, min(int(limit or 50), 200))
        log_filter = (
            'resource.type="cloud_run_revision" '
            f'AND resource.labels.service_name="{service or DEFAULT_SERVICE}"'
        )
        entries = client.list_entries(
            filter_=log_filter,
            order_by=google.cloud.logging.DESCENDING,
            page_size=limit,
            max_results=limit,
        )
        items = []
        for entry in entries:
            items.append({
                "timestamp": entry.timestamp.isoformat() if entry.timestamp else None,
                "severity": entry.severity,
                "payload": str(entry.payload)[:4000],
            })
        return {
            "status": "ok",
            "project_id": project,
            "service": service or DEFAULT_SERVICE,
            "limit": limit,
            "count": len(items),
            "entries": items,
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "type": type(exc).__name__,
            "service": service or DEFAULT_SERVICE,
        }


def secret_manager_read(secret_name: str, project_id: str | None = None, version: str = "latest") -> Dict[str, Any]:
    """Read Secret Manager metadata and optionally value hash-safe metadata only.

    This function intentionally does not return raw secret values.
    """
    if not secret_name:
        return {"status": "error", "message": "secret_name is required"}
    try:
        from google.cloud import secretmanager

        project = _google_project_id(project_id)
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project}/secrets/{secret_name}/versions/{version or 'latest'}"
        response = client.access_secret_version(request={"name": name})
        payload = response.payload.data or b""
        return {
            "status": "ok",
            "project_id": project,
            "secret_name": secret_name,
            "version": version or "latest",
            "value_present": bool(payload),
            "value_size": len(payload),
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "type": type(exc).__name__,
            "secret_name": secret_name,
        }


def secret_manager_write(secret_name: str, value: str, project_id: str | None = None) -> Dict[str, Any]:
    """Create a secret if needed and add a new version."""
    if not secret_name:
        return {"status": "error", "message": "secret_name is required"}
    if value is None or value == "":
        return {"status": "error", "message": "value is required"}
    try:
        from google.cloud import secretmanager
        from google.api_core.exceptions import AlreadyExists, NotFound

        project = _google_project_id(project_id)
        client = secretmanager.SecretManagerServiceClient()
        parent = f"projects/{project}"
        secret_path = f"{parent}/secrets/{secret_name}"

        try:
            client.get_secret(request={"name": secret_path})
            created = False
        except NotFound:
            client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": secret_name,
                    "secret": {"replication": {"automatic": {}}},
                }
            )
            created = True
        except AlreadyExists:
            created = False

        version = client.add_secret_version(
            request={
                "parent": secret_path,
                "payload": {"data": value.encode("utf-8")},
            }
        )
        return {
            "status": "ok",
            "project_id": project,
            "secret_name": secret_name,
            "created": created,
            "version": version.name,
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "type": type(exc).__name__,
            "secret_name": secret_name,
        }


def cloud_run_secret_bind(
    env_var: str,
    secret_name: str,
    service: str = DEFAULT_SERVICE,
    region: str = DEFAULT_REGION,
    version: str = "latest",
) -> Dict[str, Any]:
    """Bind a Secret Manager secret to Cloud Run env var."""
    if not env_var or not secret_name:
        return {"status": "error", "message": "env_var and secret_name are required"}
    service_q = shlex.quote(service or DEFAULT_SERVICE)
    region_q = shlex.quote(region or DEFAULT_REGION)
    binding = shlex.quote(f"{env_var}={secret_name}:{version or 'latest'}")
    command = f"gcloud run services update {service_q} --region={region_q} --update-secrets={binding}"
    return shell_exec(command, timeout=1800)


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
