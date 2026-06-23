"""Compatibility wrapper for the main AI runtime.

Runtime logic lives in services.ai_runtime.
This module remains only to avoid breaking existing imports.
"""

from services.ai_runtime import AIRuntime, RuntimeTask, ai_runtime

__all__ = ["AIRuntime", "RuntimeTask", "ai_runtime"]
