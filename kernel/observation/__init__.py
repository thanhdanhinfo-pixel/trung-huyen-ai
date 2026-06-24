"""Observation framework for TRUNG_HUYEN_AI_OS.

Observers collect facts from real system sources and normalize them into
SystemNode/SystemRelationship objects for the Kernel Digital Twin.
"""

from .observation_result import ObservationResult
from .repository_observer import repository_observer
from .runtime_observer import runtime_observer
from .tool_observer import tool_observer
from .system_observer import system_observer

__all__ = [
    "ObservationResult",
    "repository_observer",
    "runtime_observer",
    "tool_observer",
    "system_observer",
]
