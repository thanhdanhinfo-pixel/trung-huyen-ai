from __future__ import annotations

import os
from typing import Any, Callable
from brain.bootstrap import bootstrap_brain


async def run_startup_boot(boot: Callable[[], Any], production_scheduler: Any) -> None:
    brain_status = bootstrap_brain()
    print('=== LIVING_BRAIN BOOTSTRAP ===', brain_status)

    full_boot_enabled = os.getenv("ENABLE_FULL_BOOT", "false").lower() == "true"

    if not full_boot_enabled:
        print("=== SAFE STARTUP MODE ===")
        print("boot() and production_scheduler.start() disabled by ENABLE_FULL_BOOT=false")
        return

    print("=== FULL STARTUP MODE ===")
    try:
        boot()
    except Exception as exc:
        print("boot() failed:", type(exc).__name__, str(exc))

    try:
        production_scheduler.start()
    except Exception as exc:
        print("production_scheduler.start() failed:", type(exc).__name__, str(exc))
