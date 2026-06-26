"""Safe lifecycle hooks for TRUNG_HUYEN_AI_OS.

This module must never block Cloud Run startup. Boot and scheduler errors are
logged but not allowed to prevent the application from listening on PORT=8080.
"""

try:
    from system.bootstrap import boot
except Exception as exc:
    print("Lifecycle boot import failed:", exc)

    def boot():
        return None

try:
    from system.production_scheduler import production_scheduler
except Exception as exc:
    print("Lifecycle scheduler import failed:", exc)

    class _NoopScheduler:
        def start(self):
            return None

    production_scheduler = _NoopScheduler()


async def startup():
    try:
        boot()
        print("BOOT_OK")
    except Exception as exc:
        print("BOOT_FAILED:", type(exc).__name__, str(exc))

    try:
        production_scheduler.start()
        print("SCHEDULER_OK")
    except Exception as exc:
        print("SCHEDULER_FAILED:", type(exc).__name__, str(exc))
