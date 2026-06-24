from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .observation_result import ObservationResult


@dataclass
class RuntimeObserver:
    """Observe live Kernel runtime state.

    V1 is defensive: it inspects common runtime methods/attributes without
    assuming one fixed Runtime implementation.
    """

    source: str = "runtime"

    def observe(self, kernel: Any) -> ObservationResult:
        runtime = getattr(kernel, "runtime", None)
        metrics: Dict[str, Any] = {
            "runtime_available": runtime is not None,
            "runtime_type": type(runtime).__name__ if runtime is not None else None,
        }
        warnings = []

        if runtime is None:
            warnings.append({"code": "RUNTIME_NOT_AVAILABLE"})
            return ObservationResult(source=self.source, status="warning", metrics=metrics, warnings=warnings)

        for attr in ["status", "queue", "tasks", "tick_count", "last_tick", "started_at"]:
            if hasattr(runtime, attr):
                value = getattr(runtime, attr)
                if callable(value):
                    try:
                        value = value()
                    except Exception as exc:
                        warnings.append({"code": "RUNTIME_ATTRIBUTE_FAILED", "attribute": attr, "message": str(exc)})
                        continue
                metrics[attr] = self._safe_value(value)

        for method in ["status", "health", "to_dict", "summary"]:
            candidate = getattr(runtime, method, None)
            if callable(candidate):
                try:
                    metrics[f"runtime_{method}"] = self._safe_value(candidate())
                    break
                except Exception as exc:
                    warnings.append({"code": "RUNTIME_METHOD_FAILED", "method": method, "message": str(exc)})

        return ObservationResult(
            source=self.source,
            status="ok" if not warnings else "warning",
            metrics=metrics,
            warnings=warnings,
        )

    def _safe_value(self, value: Any) -> Any:
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, dict):
            return value
        if isinstance(value, (list, tuple, set)):
            return list(value)
        if hasattr(value, "to_dict") and callable(value.to_dict):
            return value.to_dict()
        return str(value)


runtime_observer = RuntimeObserver()
