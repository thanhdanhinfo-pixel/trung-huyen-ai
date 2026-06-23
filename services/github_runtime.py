from __future__ import annotations

import base64
import difflib
import os
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")

BASE = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class GitHubRuntimeError(RuntimeError):
    pass


class GitHubRuntime:
    """Stable GitHub runtime for TRUNG_HUYEN_AI_OS.

    This is the primary GitHub path for the backend. MCP should be treated as a
    secondary tool only.
    """

    def __init__(self, attempts: int = 3, delay_seconds: float = 0.5) -> None:
        self.attempts = attempts
        self.delay_seconds = delay_seconds
        self.last_success_at: Optional[str] = None
        self.last_error: Optional[str] = None
        self.last_commit_sha: Optional[str] = None

    def headers(self) -> Dict[str, str]:
        if not GITHUB_TOKEN:
            raise GitHubRuntimeError("Missing GITHUB_TOKEN environment variable.")
        return {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def run_with_retry(self, fn: Callable[[], Any]) -> Any:
        last_exc: Optional[Exception] = None
        for attempt in range(1, self.attempts + 1):
            try:
                result = fn()
                self.last_error = None
                self.last_success_at = utc_now()
                return result
            except requests.HTTPError as exc:
                last_exc = exc
                status = exc.response.status_code if exc.response is not None else 0
                if status not in {429, 500, 502, 503, 504}:
                    self.last_error = f"GitHubHTTPError {status}: {exc}"
                    raise
            except Exception as exc:  # noqa: BLE001
                last_exc = exc

            if attempt < self.attempts:
                time.sleep(self.delay_seconds)

        self.last_error = f"{type(last_exc).__name__}: {last_exc}"
        raise last_exc  # type: ignore[misc]

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ok" if GITHUB_TOKEN and GITHUB_OWNER and GITHUB_REPO else "not_configured",
            "owner": GITHUB_OWNER,
            "repo": GITHUB_REPO,
            "branch": GITHUB_BRANCH,
            "token_configured": bool(GITHUB_TOKEN),
            "last_success_at": self.last_success_at,
            "last_error": self.last_error,
        }

    def list_files(self, path: str = "") -> Any:
        def request():
            response = requests.get(
                f"{BASE}/contents/{path}",
                headers=self.headers(),
                params={"ref": GITHUB_BRANCH},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()

        return self.run_with_retry(request)

    def read_file(self, path: str) -> Dict[str, Any]:
        def request():
            response = requests.get(
                f"{BASE}/contents/{path}",
                headers=self.headers(),
                params={"ref": GITHUB_BRANCH},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return {
                "path": path,
                "sha": data.get("sha"),
                "content": base64.b64decode(data.get("content", "")).decode(),
                "encoding": data.get("encoding"),
                "size": data.get("size"),
                "html_url": data.get("html_url"),
            }

        return self.run_with_retry(request)

    def update_file(
        self,
        path: str,
        content: str,
        message: str,
        sha: Optional[str] = None,
    ) -> Dict[str, Any]:
        def request():
            resolved_sha = sha
            if not resolved_sha:
                try:
                    resolved_sha = self.read_file(path).get("sha")
                except requests.HTTPError as exc:
                    if exc.response is None or exc.response.status_code != 404:
                        raise
                    resolved_sha = None

            body: Dict[str, Any] = {
                "message": message,
                "content": base64.b64encode(content.encode()).decode(),
                "branch": GITHUB_BRANCH,
            }
            if resolved_sha:
                body["sha"] = resolved_sha

            response = requests.put(
                f"{BASE}/contents/{path}",
                headers=self.headers(),
                json=body,
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            parent_sha = result.get("commit", {}).get("parents", [{}])[0].get("sha")
            if parent_sha:
                self.last_commit_sha = parent_sha
            return result

        return self.run_with_retry(request)

    def patch_file(
        self,
        path: str,
        operations: List[Dict[str, str]],
        message: str = "Safe patch update",
        commit: bool = False,
    ) -> Dict[str, Any]:
        current = self.read_file(path)
        old_content = current.get("content", "")
        new_content = old_content

        for op in operations:
            op_type = op.get("type", "")
            find = op.get("find", "")
            replace = op.get("replace", "")

            if op_type == "replace":
                if not find or find not in new_content:
                    return {"status": "error", "message": "find text not found"}
                new_content = new_content.replace(find, replace, 1)
            elif op_type == "insert_after":
                if not find or find not in new_content:
                    return {"status": "error", "message": "anchor text not found"}
                new_content = new_content.replace(find, find + replace, 1)
            elif op_type == "insert_before":
                if not find or find not in new_content:
                    return {"status": "error", "message": "anchor text not found"}
                new_content = new_content.replace(find, replace + find, 1)
            elif op_type == "delete":
                if not find or find not in new_content:
                    return {"status": "error", "message": "delete text not found"}
                new_content = new_content.replace(find, "", 1)
            elif op_type == "append":
                new_content = new_content + replace
            elif op_type == "prepend":
                new_content = replace + new_content
            else:
                return {"status": "error", "message": f"Unsupported operation: {op_type}"}

        before_lines = old_content.splitlines()
        after_lines = new_content.splitlines()
        warnings: List[str] = []

        if len(after_lines) < len(before_lines) * 0.8:
            warnings.append("line_count_drop_over_20_percent")
        if "APIRouter" in old_content and "APIRouter" not in new_content:
            warnings.append("possible_router_import_removed")
        if "@router." in old_content and "@router." not in new_content:
            warnings.append("possible_endpoint_loss")

        diff = "\n".join(
            difflib.unified_diff(
                before_lines,
                after_lines,
                fromfile=f"before/{path}",
                tofile=f"after/{path}",
                lineterm="",
            )
        )

        result: Dict[str, Any] = {
            "status": "preview",
            "path": path,
            "changed": new_content != old_content,
            "warnings": warnings,
            "ready_to_commit": new_content != old_content and not warnings,
            "diff": diff,
        }

        if not commit:
            return result

        if warnings:
            return {"status": "blocked", "warnings": warnings, "diff": diff}
        if new_content == old_content:
            return {"status": "noop", "message": "Patch produced no changes"}

        commit_result = self.update_file(
            path=path,
            content=new_content,
            message=message,
            sha=current.get("sha"),
        )

        verified = False
        for _ in range(5):
            time.sleep(0.5)
            verify = self.read_file(path)
            if verify.get("content") == new_content:
                verified = True
                break

        return {
            "status": "committed",
            "path": path,
            "commit": commit_result.get("commit", {}),
            "verified": verified,
        }


github_runtime = GitHubRuntime()
