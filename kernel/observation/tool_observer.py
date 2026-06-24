from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from services.github_runtime import github_runtime
from .observation_result import ObservationResult


@dataclass
class ToolObserver:
    source: str = "tools"

    def observe(self, kernel: Any) -> ObservationResult:
        registry = getattr(kernel, "registry", None)
        capabilities = getattr(kernel, "capabilities", None)
        repository_adapter = getattr(kernel, "repository_adapter", None)

        metrics: Dict[str, Any] = {
            "registry_available": registry is not None,
            "capabilities_available": capabilities is not None,
            "repository_adapter_available": repository_adapter is not None,
        }

        warnings = []

        if repository_adapter is not None:
            try:
                metrics["repository_adapter_status"] = repository_adapter.status()
            except Exception as exc:
                warnings.append({"code": "REPOSITORY_ADAPTER_STATUS_FAILED", "message": str(exc)})

        github_status = {"configured": False, "read_ok": False, "error": None}

        try:
            status = github_runtime.status()
            github_status["configured"] = status.get("status") == "ok"
            github_runtime.read_file("kernel/system_model.py")
            github_status["read_ok"] = True
        except Exception as exc:
            github_status["error"] = str(exc)

        metrics["github"] = github_status

        if not github_status["configured"]:
            warnings.append({"code": "GITHUB_NOT_CONFIGURED"})
        if not github_status["read_ok"]:
            warnings.append({"code": "GITHUB_READ_FAILED"})
        if registry is None:
            warnings.append({"code": "REGISTRY_NOT_AVAILABLE"})
        if capabilities is None:
            warnings.append({"code": "CAPABILITIES_NOT_AVAILABLE"})

        return ObservationResult(source=self.source, status="ok" if not warnings else "warning", metrics=metrics, warnings=warnings)


tool_observer = ToolObserver()
