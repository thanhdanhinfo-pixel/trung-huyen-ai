import os
import base64
from typing import Any, Dict, List

import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")

print("===== GITHUB CONFIG =====")
print("TOKEN CONFIGURED:", bool(GITHUB_TOKEN))
print("OWNER CONFIGURED:", bool(GITHUB_OWNER))
print("REPO CONFIGURED:", bool(GITHUB_REPO))
print("BRANCH:", GITHUB_BRANCH)
print("=========================")

BASE = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"


def _headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }


def _encode_content(content: str) -> str:
    return base64.b64encode(content.encode()).decode()


def github_list_files(path=""):
    r = requests.get(
        f"{BASE}/contents/{path}",
        headers=_headers(),
        params={"ref": GITHUB_BRANCH},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def github_read_file(path):
    r = requests.get(
        f"{BASE}/contents/{path}",
        headers=_headers(),
        params={"ref": GITHUB_BRANCH},
        timeout=30,
    )
    r.raise_for_status()

    data = r.json()

    return {
        "path": path,
        "sha": data["sha"],
        "content": base64.b64decode(data["content"]).decode(),
    }


def github_file_exists(path: str) -> Dict[str, Any] | None:
    try:
        return github_read_file(path)
    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 404:
            return None
        raise


def github_create_file(path: str, content: str, message: str):
    existing = github_file_exists(path)
    if existing:
        raise ValueError(f"File already exists: {path}")

    body = {
        "message": message,
        "content": _encode_content(content),
        "branch": GITHUB_BRANCH,
    }

    r = requests.put(
        f"{BASE}/contents/{path}",
        headers=_headers(),
        json=body,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def github_update_file(path, content, sha, message):
    body = {
        "message": message,
        "content": _encode_content(content),
        "sha": sha,
        "branch": GITHUB_BRANCH,
    }

    r = requests.put(
        f"{BASE}/contents/{path}",
        headers=_headers(),
        json=body,
        timeout=30,
    )

    r.raise_for_status()

    return r.json()


def github_upsert_file(path: str, content: str, message: str):
    existing = github_file_exists(path)
    if existing:
        return github_update_file(path, content, existing["sha"], message)
    return github_create_file(path, content, message)


def github_delete_file(path: str, message: str):
    existing = github_file_exists(path)
    if not existing:
        raise ValueError(f"File not found: {path}")

    body = {
        "message": message,
        "sha": existing["sha"],
        "branch": GITHUB_BRANCH,
    }

    r = requests.delete(
        f"{BASE}/contents/{path}",
        headers=_headers(),
        json=body,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def github_batch_update(message: str, operations: List[Dict[str, Any]]):
    """Execute a batch of GitHub content operations.

    This implementation uses GitHub Contents API sequentially. That means each
    operation may create its own GitHub commit. The returned report is the
    stable execution contract. A future implementation can replace this with
    Git Data API to produce one atomic commit without changing callers.
    """
    results: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    for index, operation in enumerate(operations):
        op_type = (operation.get("type") or "upsert").lower()
        path = operation.get("path") or ""
        content = operation.get("content", "")
        op_message = operation.get("message") or f"{message} ({index + 1}/{len(operations)})"

        if not path:
            errors.append({
                "index": index,
                "type": op_type,
                "path": path,
                "error_type": "ValidationError",
                "message": "path is required",
            })
            continue

        try:
            if op_type == "create":
                result = github_create_file(path, content, op_message)
            elif op_type == "update":
                existing = github_file_exists(path)
                if not existing:
                    raise ValueError(f"File not found for update: {path}")
                result = github_update_file(path, content, existing["sha"], op_message)
            elif op_type == "delete":
                result = github_delete_file(path, op_message)
            elif op_type in {"upsert", "write"}:
                result = github_upsert_file(path, content, op_message)
            else:
                raise ValueError(f"Unsupported operation type: {op_type}")

            results.append({
                "index": index,
                "type": op_type,
                "path": path,
                "status": "ok",
                "result": result,
            })
        except Exception as exc:
            errors.append({
                "index": index,
                "type": op_type,
                "path": path,
                "status": "error",
                "error_type": type(exc).__name__,
                "message": str(exc),
            })

    return {
        "status": "ok" if not errors else "partial_error",
        "message": message,
        "total": len(operations),
        "succeeded": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors,
    }
