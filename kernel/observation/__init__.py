"""Observation framework for TRUNG_HUYEN_AI_OS.

Observers collect facts from real system sources and normalize them into
SystemNode/SystemRelationship objects for the Kernel Digital Twin.
"""

from .observation_result import ObservationResult
from .repository_observer import repository_observer
from .system_observer import system_observer

__all__ = ["ObservationResult", "repository_observer", "system_observer"]
