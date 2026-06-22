from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RuntimeHealth:
    def __init__(self) -> None:
        self.last_checked_at: Optional[str] = None
        self.components: Dict[str, Dict[str, Any]] = {}

    def check(self, name: str, check_fn: Callable[[], Any]) -> Dict[str, Any]:
        checked_at = utc_now()
        try:
            result = check_fn()
            state = {
                "status": "ok",
                "checked_at": checked_at,
                "error": None,
                "result": result,
            }
        except Exception as exc:  # noqa: BLE001
            state = {
                "status": "error",
                "checked_at": checked_at,
                "error": f"{type(exc).__name__}: {exc}",
                "result": None,
            }
        self.components[name] = state
        self.last_checked_at = checked_at
        return state

    def status(self) -> Dict[str, Any]:
        overall = "ok"
        if any(item.get("status") == "error" for item in self.components.values()):
            overall = "degraded"
        return {
            "status": overall,
            "checked_at": self.last_checked_at or utc_now(),
            "components": self.components,
        }


runtime_health = RuntimeHealth()
