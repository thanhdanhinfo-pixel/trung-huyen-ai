from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests

DEFAULT_BASE_URL = "https://trung-huyen-ai-779121307308.asia-southeast1.run.app"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class HealthRuntime:
    def __init__(self, base_url: str = DEFAULT_BASE_URL) -> None:
        self.base_url = base_url.rstrip("/")
        self.last_report: Optional[Dict[str, Any]] = None

    def check_get(self, path: str, timeout: int = 20) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        checked_at = utc_now()
        try:
            response = requests.get(url, timeout=timeout)
            ok = 200 <= response.status_code < 300
            payload: Any
            try:
                payload = response.json()
            except Exception:
                payload = response.text[:500]
            return {
                "path": path,
                "url": url,
                "method": "GET",
                "ok": ok,
                "status_code": response.status_code,
                "checked_at": checked_at,
                "response": payload,
                "error": None,
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "path": path,
                "url": url,
                "method": "GET",
                "ok": False,
                "status_code": None,
                "checked_at": checked_at,
                "response": None,
                "error": f"{type(exc).__name__}: {exc}",
            }

    def self_test(self) -> Dict[str, Any]:
        checks: List[Dict[str, Any]] = [
            self.check_get("/health"),
            self.check_get("/system/runtime/status"),
            self.check_get("/system/runtime/tasks"),
            self.check_get("/system/runtime/health"),
        ]
        report = {
            "status": "ok" if all(item["ok"] for item in checks) else "degraded",
            "checked_at": utc_now(),
            "base_url": self.base_url,
            "checks": checks,
        }
        self.last_report = report
        return report


health_runtime = HealthRuntime()
