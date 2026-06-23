from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

from services.github_runtime import github_runtime


MAX_ROOT_PY_FILES = 15
MAX_LARGE_FILE_SIZE = 20_000
REQUIRED_FOLDERS = [
    "api",
    "services",
    "docs",
    "core",
    "brain",
    "organization",
    "runtime",
    "security",
    "monitoring",
    "memory",
    "knowledge",
    "connectors",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RepositoryHealthReport:
    status: str
    score: int
    created_at: str = field(default_factory=utc_now)
    checks: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RepositoryHealthMonitor:
    """Trung tâm giám sát sức khỏe repository.

    Chấm điểm repository theo tiêu chí bền vững: cấu trúc thư mục, số file ở root,
    file quá lớn, file sinh tự động, và mức độ tuân thủ kiến trúc Trung Huyền OS.
    """

    def __init__(self) -> None:
        self.last_report: Dict[str, Any] = {}

    def check(self) -> Dict[str, Any]:
        root = github_runtime.list_files("")
        if not isinstance(root, list):
            return {"status": "failed", "message": "Không đọc được repository root"}

        checks: List[Dict[str, Any]] = []
        recommendations: List[str] = []
        score = 100

        folders = sorted(item.get("name") for item in root if item.get("type") == "dir")
        files = [item for item in root if item.get("type") == "file"]
        root_py = [item for item in files if item.get("name", "").endswith(".py")]
        pyc_files = [item for item in files if item.get("name", "").endswith(".pyc")]
        large_files = [item for item in files if int(item.get("size") or 0) > MAX_LARGE_FILE_SIZE]
        missing_folders = [folder for folder in REQUIRED_FOLDERS if folder not in folders]

        if len(root_py) > MAX_ROOT_PY_FILES:
            penalty = min(30, len(root_py) - MAX_ROOT_PY_FILES)
            score -= penalty
            recommendations.append("Giảm số file Python ở thư mục gốc bằng cách di chuyển vào các module chuẩn.")
        checks.append({
            "name": "root_python_files",
            "status": "ok" if len(root_py) <= MAX_ROOT_PY_FILES else "warning",
            "count": len(root_py),
            "limit": MAX_ROOT_PY_FILES,
        })

        if pyc_files:
            score -= min(20, len(pyc_files) * 5)
            recommendations.append("Xóa toàn bộ file .pyc và đảm bảo .gitignore chặn file sinh tự động.")
        checks.append({
            "name": "compiled_python_files",
            "status": "ok" if not pyc_files else "warning",
            "count": len(pyc_files),
            "files": [item.get("path") for item in pyc_files],
        })

        if large_files:
            score -= min(20, len(large_files) * 4)
            recommendations.append("Tách các file lớn thành module nhỏ để dễ bảo trì.")
        checks.append({
            "name": "large_root_files",
            "status": "ok" if not large_files else "warning",
            "count": len(large_files),
            "files": [item.get("path") for item in large_files],
        })

        if missing_folders:
            score -= min(30, len(missing_folders) * 3)
            recommendations.append("Tạo đủ các thư mục trụ cột của Trung Huyền OS để thống nhất kiến trúc.")
        checks.append({
            "name": "required_foundation_folders",
            "status": "ok" if not missing_folders else "warning",
            "missing": missing_folders,
        })

        score = max(0, min(100, score))
        status = "healthy" if score >= 85 else "needs_attention" if score >= 60 else "critical"
        report = RepositoryHealthReport(
            status=status,
            score=score,
            checks=checks,
            recommendations=recommendations,
        ).to_dict()
        self.last_report = report
        return report

    def latest(self) -> Dict[str, Any]:
        return self.last_report or self.check()


repository_health_monitor = RepositoryHealthMonitor()
