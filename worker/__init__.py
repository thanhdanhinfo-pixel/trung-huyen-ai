"""AI Worker package.

The Worker is the execution runtime for TRUNG_HUYEN_AI_OS.
It runs work in explicit ticks so it can operate in Cloud Run,
Cloud Scheduler, GitHub Actions, Docker, or a future daemon loop.
"""

from .main import AIWorker, worker

__all__ = ["AIWorker", "worker"]
