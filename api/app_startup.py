from __future__ import annotations

import os
from typing import Any, Callable


async def run_startup_boot(boot: Callable[[], Any], production_scheduler: Any) -> None:
    """Application startup coordinator.

    Full boot remains feature-flagged to preserve Cloud Run production safety.
    Set ENABLE_FULL_BOOT=true to enable boot() and production_scheduler.start().
    """
    full_boot_enabled = os.getenv("ENABLE_FULL_BOOT", "false").lower() == "true"

    if not full_boot_enabled:
        print("=== SAFE STARTUP MODE ===")
        print("boot() and production_scheduler.start() disabled by ENABLE_FULL_BOOT=false")
        return

    print("=== FULL STARTUP MODE ===")
    try:
        boot()
    except Exception as exc:  # noqa: BLE001
        print("boot() failed:", type(exc).__name__, str(exc))

    try:
        production_scheduler.start()
    except Exception as exc:  # noqa: BLE001
        print("production_scheduler.start() failed:", type(exc).__name__, str(exc))
