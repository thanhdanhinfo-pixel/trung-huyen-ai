from __future__ import annotations

import os
import traceback
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

from services.github_runtime import github_runtime


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class DiagnosticStep:
    name: str
    status: str
    detail: Dict[str, Any] = field(default_factory=dict)
    error_type: str | None = None
    error_message: str | None = None
    traceback: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RuntimeDiagnostic:
    """Chẩn đoán Runtime để tìm chính xác lỗi ghi GitHub/Cloud Run."""

    def version(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "service": "TRUNG_HUYEN_AI_OS",
            "diagnostic_version": "1.0.0",
            "created_at": utc_now(),
            "github_owner": os.getenv("GITHUB_OWNER"),
            "github_repo": os.getenv("GITHUB_REPO"),
            "github_branch": os.getenv("GITHUB_BRANCH", "main"),
            "github_token_configured": bool(os.getenv("GITHUB_TOKEN")),
            "cloud_run_revision": os.getenv("K_REVISION"),
            "cloud_run_service": os.getenv("K_SERVICE"),
            "cloud_run_configuration": os.getenv("K_CONFIGURATION"),
        }

    def github_status(self) -> Dict[str, Any]:
        try:
            return {
                "status": "ok",
                "runtime_status": github_runtime.status(),
            }
        except Exception as exc:  # noqa: BLE001
            return self._error("github_status", exc).to_dict()

    def github_write_selftest(self) -> Dict[str, Any]:
        path = f"diagnostics/RUNTIME_WRITE_SELFTEST_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
        content_1 = f"# Runtime Write Self Test\n\nCreated at: {utc_now()}\n"
        content_2 = content_1 + "\nUpdated: true\n"
        steps: List[DiagnosticStep] = []

        try:
            result = github_runtime.update_file(
                path=path,
                content=content_1,
                message="Diagnostic: create runtime write selftest",
            )
            steps.append(DiagnosticStep("create_file", "ok", {"path": path, "commit": result.get("commit", {})}))
        except Exception as exc:  # noqa: BLE001
            steps.append(self._error("create_file", exc))
            return self._report(path, steps)

        try:
            read = github_runtime.read_file(path)
            steps.append(DiagnosticStep("read_created_file", "ok", {"sha": read.get("sha"), "size": read.get("size")}))
        except Exception as exc:  # noqa: BLE001
            steps.append(self._error("read_created_file", exc))
            return self._report(path, steps)

        try:
            current = github_runtime.get_file_metadata(path)
            result = github_runtime.update_file(
                path=path,
                content=content_2,
                message="Diagnostic: update runtime write selftest",
                sha=current.get("sha"),
            )
            steps.append(DiagnosticStep("update_file", "ok", {"path": path, "commit": result.get("commit", {})}))
        except Exception as exc:  # noqa: BLE001
            steps.append(self._error("update_file", exc))
            return self._report(path, steps)

        try:
            deleted = github_runtime.delete_file(path, message="Diagnostic: delete runtime write selftest")
            steps.append(DiagnosticStep("delete_file", "ok", {"path": path, "commit": deleted.get("commit", {})}))
        except Exception as exc:  # noqa: BLE001
            steps.append(self._error("delete_file", exc))
            return self._report(path, steps)

        return self._report(path, steps)

    def _report(self, path: str, steps: List[DiagnosticStep]) -> Dict[str, Any]:
        failed = [step for step in steps if step.status != "ok"]
        return {
            "status": "failed" if failed else "ok",
            "path": path,
            "created_at": utc_now(),
            "steps": [step.to_dict() for step in steps],
        }

    def _error(self, name: str, exc: Exception) -> DiagnosticStep:
        detail: Dict[str, Any] = {}
        response = getattr(exc, "response", None)
        if response is not None:
            detail = {
                "http_status": getattr(response, "status_code", None),
                "response_text": getattr(response, "text", ""),
                "response_headers": dict(getattr(response, "headers", {}) or {}),
            }
        return DiagnosticStep(
            name=name,
            status="failed",
            detail=detail,
            error_type=type(exc).__name__,
            error_message=str(exc),
            traceback=traceback.format_exc(),
        )


runtime_diagnostic = RuntimeDiagnostic()
