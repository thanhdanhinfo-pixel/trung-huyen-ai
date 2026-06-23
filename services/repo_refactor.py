from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from services.dependency_analyzer import dependency_analyzer
from services.github_runtime import github_runtime
from services.safe_move_engine import safe_move_engine


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RepoRefactorRun:
    id: str
    status: str = "created"
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    analysis: Dict[str, Any] = field(default_factory=dict)
    move_plan: Dict[str, Any] = field(default_factory=dict)
    preview: Dict[str, Any] = field(default_factory=dict)
    result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def update(self, status: str, data: Optional[Dict[str, Any]] = None) -> None:
        self.status = status
        self.updated_at = utc_now()
        if data:
            for key, value in data.items():
                setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RepoRefactor:
    """Repository refactor orchestrator.

    Owns the safe flow:
    analyze -> move plan -> preview -> execute small batch -> verify.
    """

    def __init__(self) -> None:
        self.runs: List[RepoRefactorRun] = []

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "runtime": "repo_refactor",
            "run_count": len(self.runs),
            "latest": self.runs[-1].to_dict() if self.runs else None,
        }

    def analyze(self) -> Dict[str, Any]:
        analysis = dependency_analyzer.analyze()
        move_plan = dependency_analyzer.move_plan()
        return {"status": "ok", "analysis": analysis, "move_plan": move_plan}

    def move_plan(self, limit: int = 10) -> Dict[str, Any]:
        plan = dependency_analyzer.move_plan()
        operations = plan.get("operations", [])[:limit]
        return {
            "status": "ok",
            "operation_count": len(operations),
            "operations": operations,
            "total_available": plan.get("operation_count", 0),
        }

    def preview(self, limit: int = 5) -> Dict[str, Any]:
        run = RepoRefactorRun(id=f"repo-refactor-{len(self.runs) + 1:04d}")
        self.runs.append(run)
        analysis = dependency_analyzer.analyze()
        plan = dependency_analyzer.move_plan()
        operations = plan.get("operations", [])[:limit]
        preview = safe_move_engine.preview(operations)
        run.update("preview", {"analysis": analysis, "move_plan": plan, "preview": preview})
        return {"status": "preview", "run": run.to_dict()}

    def execute(self, limit: int = 3, import_file_limit: int = 50) -> Dict[str, Any]:
        run = RepoRefactorRun(id=f"repo-refactor-{len(self.runs) + 1:04d}")
        self.runs.append(run)
        run.update("running")
        try:
            analysis = dependency_analyzer.analyze()
            plan = dependency_analyzer.move_plan()
            operations = plan.get("operations", [])[:limit]
            import_files = analysis.get("root_python_files", [])[:import_file_limit]
            import_files += [
                module.get("path")
                for module in analysis.get("modules", [])
                if module.get("path") and "/" in module.get("path")
            ][:import_file_limit]
            result = safe_move_engine.execute(
                operations=operations,
                import_files=sorted(set(import_files)),
                message="Repository refactor batch",
            )
            verify = self.verify()
            run.update(
                "done" if result.get("status") == "done" and verify.get("status") == "ok" else "partial_failure",
                {"analysis": analysis, "move_plan": plan, "result": {"move": result, "verify": verify}},
            )
            return {"status": run.status, "run": run.to_dict()}
        except Exception as exc:  # noqa: BLE001
            run.error = f"{type(exc).__name__}: {exc}"
            run.update("failed")
            return {"status": "failed", "run": run.to_dict(), "error": run.error}

    def verify(self) -> Dict[str, Any]:
        root = github_runtime.list_files("")
        if not isinstance(root, list):
            return {"status": "failed", "message": "Cannot list repository root"}
        root_py = [item.get("path") for item in root if item.get("type") == "file" and item.get("path", "").endswith(".py")]
        return {
            "status": "ok",
            "root_python_file_count": len(root_py),
            "root_python_files": root_py,
        }

    def history(self) -> List[Dict[str, Any]]:
        return [run.to_dict() for run in self.runs]


repo_refactor = RepoRefactor()
