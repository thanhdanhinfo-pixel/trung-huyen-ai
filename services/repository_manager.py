from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

from services.dependency_analyzer import dependency_analyzer
from services.github_runtime import github_runtime
from services.safe_move_engine import safe_move_engine


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


CORE_FOLDERS = [
    "core",
    "brain",
    "organization",
    "runtime",
    "security",
    "monitoring",
    "memory",
    "knowledge",
    "connectors",
    "api",
    "docs",
    "tests",
    "scripts",
]


@dataclass
class RepositoryPlan:
    status: str
    created_at: str = field(default_factory=utc_now)
    root_python_count: int = 0
    operations: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RepositoryManager:
    """Quản lý và tái cấu trúc repository theo kiến trúc Trung Huyền OS.

    Phiên bản nền tảng: chỉ lập kế hoạch, preview và thực thi theo lô nhỏ.
    Không di chuyển ồ ạt, không phá hệ thống đang chạy.
    """

    def __init__(self) -> None:
        self.last_plan: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "manager": "repository_manager",
            "core_folders": CORE_FOLDERS,
            "has_last_plan": bool(self.last_plan),
            "history_count": len(self.history),
        }

    def analyze(self) -> Dict[str, Any]:
        analysis = dependency_analyzer.analyze()
        root = github_runtime.list_files("")
        folders = sorted(
            item.get("name") for item in root
            if isinstance(root, list) and item.get("type") == "dir"
        )
        missing_folders = [folder for folder in CORE_FOLDERS if folder not in folders]
        return {
            "status": "ok",
            "analysis": analysis,
            "existing_folders": folders,
            "missing_folders": missing_folders,
        }

    def make_plan(self, limit: int = 10) -> Dict[str, Any]:
        analysis = self.analyze()
        move_plan = dependency_analyzer.move_plan()
        operations = move_plan.get("operations", [])[:limit]
        plan = RepositoryPlan(
            status="preview",
            root_python_count=analysis.get("analysis", {}).get("root_python_file_count", 0),
            operations=operations,
            warnings=[
                "Chỉ thực thi theo batch nhỏ.",
                "Không di chuyển app.py, config.py, Dockerfile, requirements.txt trong giai đoạn nền tảng.",
                "Mọi thay đổi phải qua preview trước khi commit.",
            ],
        ).to_dict()
        self.last_plan = plan
        return plan

    def preview(self, limit: int = 5) -> Dict[str, Any]:
        plan = self.make_plan(limit=limit)
        preview = safe_move_engine.preview(plan.get("operations", []))
        return {
            "status": "preview",
            "plan": plan,
            "preview": preview,
        }

    def execute(self, limit: int = 3, import_file_limit: int = 50) -> Dict[str, Any]:
        analysis = dependency_analyzer.analyze()
        plan = self.make_plan(limit=limit)
        operations = plan.get("operations", [])
        import_files = analysis.get("root_python_files", [])[:import_file_limit]
        import_files += [
            module.get("path")
            for module in analysis.get("modules", [])
            if module.get("path") and "/" in module.get("path")
        ][:import_file_limit]
        result = safe_move_engine.execute(
            operations=operations,
            import_files=sorted(set(import_files)),
            message="Repository Manager: safe structure batch",
        )
        record = {
            "status": result.get("status"),
            "created_at": utc_now(),
            "plan": plan,
            "result": result,
            "verify": self.verify(),
        }
        self.history.append(record)
        return record

    def verify(self) -> Dict[str, Any]:
        root = github_runtime.list_files("")
        if not isinstance(root, list):
            return {"status": "failed", "message": "Không đọc được thư mục gốc repository"}
        root_py = [
            item.get("path") for item in root
            if item.get("type") == "file" and item.get("path", "").endswith(".py")
        ]
        return {
            "status": "ok",
            "root_python_file_count": len(root_py),
            "root_python_files": root_py,
        }


repository_manager = RepositoryManager()
