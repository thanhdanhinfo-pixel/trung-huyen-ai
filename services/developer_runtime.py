from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

from services.github_runtime import github_runtime


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class DeveloperRuntimeRecord:
    id: str
    status: str
    created_at: str = field(default_factory=utc_now)
    operation_count: int = 0
    results: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DeveloperRuntime:
    """Bộ thực thi phát triển cho Trung Huyền OS.

    Mục tiêu: nhận nhiều thay đổi, preview/patch/verify/rollback theo một luồng
    thống nhất thay vì sửa từng file thủ công.
    """

    def __init__(self) -> None:
        self.records: List[DeveloperRuntimeRecord] = []

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "runtime": "developer_runtime",
            "record_count": len(self.records),
            "latest": self.records[-1].to_dict() if self.records else None,
            "capabilities": [
                "patch_files",
                "batch_operations",
                "verify_paths",
                "rollback_v2_planned",
            ],
        }

    def patch(self, files: List[Dict[str, Any]], message: str = "Developer runtime patch", commit: bool = False) -> Dict[str, Any]:
        record = DeveloperRuntimeRecord(
            id=f"developer-patch-{len(self.records) + 1:04d}",
            status="preview" if not commit else "running",
            operation_count=len(files),
        )
        self.records.append(record)

        results: List[Dict[str, Any]] = []
        failed = 0
        for item in files:
            path = item.get("path", "")
            content = item.get("content", "")
            if not path:
                failed += 1
                results.append({"status": "failed", "message": "missing path"})
                continue

            if not commit:
                exists = True
                current_sha = None
                try:
                    meta = github_runtime.get_file_metadata(path)
                    current_sha = meta.get("sha")
                except Exception:
                    exists = False
                results.append({
                    "status": "preview",
                    "path": path,
                    "exists": exists,
                    "current_sha": current_sha,
                    "size": len(content),
                })
                continue

            try:
                result = github_runtime.update_file(
                    path=path,
                    content=content,
                    message=item.get("message", message),
                    sha=item.get("sha"),
                )
                results.append({"status": "committed", "path": path, "commit": result.get("commit", {})})
            except Exception as exc:  # noqa: BLE001
                failed += 1
                results.append({"status": "failed", "path": path, "error": f"{type(exc).__name__}: {exc}"})

        record.status = "done" if failed == 0 and commit else "preview" if not commit else "partial_failure"
        record.results = results
        return record.to_dict()

    def batch(self, operations: List[Dict[str, Any]], message: str = "Developer runtime batch", commit: bool = False) -> Dict[str, Any]:
        record = DeveloperRuntimeRecord(
            id=f"developer-batch-{len(self.records) + 1:04d}",
            status="preview" if not commit else "running",
            operation_count=len(operations),
        )
        self.records.append(record)

        if not commit:
            record.results = [{"status": "preview", "operation": op} for op in operations]
            return record.to_dict()

        result = github_runtime.batch_commit(operations, message=message)
        record.status = result.get("status", "unknown")
        record.results = result.get("results", [])
        return record.to_dict()

    def verify(self, paths: List[str]) -> Dict[str, Any]:
        results = []
        for path in paths:
            try:
                meta = github_runtime.get_file_metadata(path)
                results.append({"status": "ok", "path": path, "sha": meta.get("sha"), "size": meta.get("size")})
            except Exception as exc:  # noqa: BLE001
                results.append({"status": "missing", "path": path, "error": f"{type(exc).__name__}: {exc}"})
        return {"status": "ok", "results": results}

    def rollback(self) -> Dict[str, Any]:
        return {
            "status": "not_implemented",
            "message": "Rollback thật sẽ được triển khai ở Developer Runtime v2 bằng snapshot trước commit.",
        }
    def run_command(self, command: str = "") -> Dict[str, Any]:
        allowed = {
            "tools/dependency_graph.py",
            "tools/import_safety.py",
            "tools/orphan_detector.py",
            "scripts/health_check.py",
        }

        if command not in allowed:
            return {
                "status": "error",
                "message": f"Command not allowed: {command}",
                "allowed": sorted(list(allowed)),
            }

        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, command],
            shell=False,
            timeout=30,
            capture_output=True,
            text=True,
        )

        return {
            "status": "ok" if result.returncode == 0 else "failed",
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout[-4000:],
            "stderr": result.stderr[-4000:],
            "timeout": 30,
        }

    def execute(self, action: str, payload: dict) -> Dict[str, Any]:
        registry = {
            "developer.transform": self.patch,
            "developer.transaction": self.batch,
            "developer.verify": self.verify,
            "developer.run_command": self.run_command,
        }

        handler = registry.get(action)

        if not handler:
            return {
                "status": "error",
                "message": f"Unknown action: {action}",
            }

        return handler(**payload)

developer_runtime = DeveloperRuntime()
