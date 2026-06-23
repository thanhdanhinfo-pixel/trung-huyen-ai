from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict, List

from services.worker_runner import worker_runner


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class BackgroundLoop:
    """Vòng lặp chạy nền cho AI Workforce.

    V1 không tự chạy vô hạn trong web request. Runtime/Cloud Scheduler sẽ gọi
    run_once hoặc run_batch định kỳ. Khi tách sang Cloud Run Worker riêng có thể
    dùng run_forever.
    """

    def __init__(self) -> None:
        self.enabled = False
        self.tick_count = 0
        self.last_tick: Dict[str, Any] | None = None
        self.history: List[Dict[str, Any]] = []

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "service": "background_loop",
            "enabled": self.enabled,
            "tick_count": self.tick_count,
            "last_tick": self.last_tick,
            "runner": worker_runner.status(),
        }

    def enable(self) -> Dict[str, Any]:
        self.enabled = True
        return self.status()

    def disable(self) -> Dict[str, Any]:
        self.enabled = False
        return self.status()

    def tick(self, limit: int = 5, capability: str | None = None) -> Dict[str, Any]:
        self.tick_count += 1
        result = worker_runner.run_batch(limit=limit, capability=capability)
        record = {
            "status": "ok",
            "tick": self.tick_count,
            "ran_at": now(),
            "enabled": self.enabled,
            "result": result,
        }
        self.last_tick = record
        self.history.append(record)
        return record

    def run_forever(self, interval_seconds: float = 5.0, limit: int = 5) -> None:
        self.enabled = True
        while self.enabled:
            self.tick(limit=limit)
            time.sleep(max(1.0, interval_seconds))

    def recent(self, limit: int = 20) -> Dict[str, Any]:
        return {"status": "ok", "history": self.history[-limit:]}


background_loop = BackgroundLoop()
