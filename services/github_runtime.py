from __future__ import annotations

import base64
import os
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional

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
            return response.json()

        return self.run_with_retry(request)


github_runtime = GitHubRuntime()
