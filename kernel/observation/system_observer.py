from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from .observation_result import ObservationResult
from .repository_observer import repository_observer
from .runtime_observer import runtime_observer

try:
    from .tool_observer import tool_observer
except Exception:
    tool_observer = None


@dataclass
class SystemObserver:
    """Top-level observer for TRUNG_HUYEN_AI_OS.

    SystemObserver coordinates source-specific observers and returns one
    normalized system observation snapshot. This is the first layer that lets
    the Kernel observe more than repository structure.
    """

    source: str = "system"
    last_observation: Dict[str, Any] = field(default_factory=dict)

    def observe(self, kernel: Any) -> Dict[str, Any]:
        observations: Dict[str, Any] = {}
        warnings = []

        for name, observer in self._observers().items():
            if observer is None:
                warnings.append({"code": "OBSERVER_NOT_AVAILABLE", "observer": name})
                continue
            try:
                result = observer.observe(kernel)
                observations[name] = result.to_dict() if hasattr(result, "to_dict") else result
            except Exception as exc:
                warnings.append({
                    "code": "OBSERVER_FAILED",
                    "observer": name,
                    "message": str(exc),
                    "type": type(exc).__name__,
                })

        status = "ok" if not warnings else "warning"
        result = ObservationResult(
            source=self.source,
            status=status,
            metrics={
                "observer_count": len(self._observers()),
                "successful_observer_count": len(observations),
                "warning_count": len(warnings),
            },
            warnings=warnings,
        ).to_dict()
        result["observations"] = observations
        self.last_observation = result
        return result

    def status(self) -> Dict[str, Any]:
        if not self.last_observation:
            return {"status": "idle"}
        return {"status": "ok", "last_observation": self.last_observation}

    def _observers(self) -> Dict[str, Any]:
        return {
            "repository": repository_observer,
            "runtime": runtime_observer,
            "tools": tool_observer,
        }


system_observer = SystemObserver()
