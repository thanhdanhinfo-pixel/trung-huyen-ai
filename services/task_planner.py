from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class PlannedTask:
    id: str
    title: str
    capability: str
    owner: str
    priority: int = 3
    status: str = "planned"
    dependencies: List[str] = field(default_factory=list)
    acceptance: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TaskPlanner:
    """Bộ lập kế hoạch tác vụ cho Trung Huyền OS.

    Nhận mục tiêu cấp cao, chia thành task có owner, capability, priority,
    dependency và tiêu chí nghiệm thu.
    """

    def __init__(self) -> None:
        self.plans: List[Dict[str, Any]] = []

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "service": "task_planner",
            "plan_count": len(self.plans),
            "latest": self.plans[-1] if self.plans else None,
        }

    def plan(self, goal: str, capability: str = "core", priority: int = 3) -> Dict[str, Any]:
        tasks = self._default_breakdown(goal=goal, capability=capability, priority=priority)
        record = {
            "status": "planned",
            "goal": goal,
            "capability": capability,
            "created_at": utc_now(),
            "task_count": len(tasks),
            "tasks": [task.to_dict() for task in tasks],
        }
        self.plans.append(record)
        return record

    def _default_breakdown(self, goal: str, capability: str, priority: int) -> List[PlannedTask]:
        prefix = f"{capability.upper()}-{len(self.plans) + 1:04d}"
        return [
            PlannedTask(
                id=f"{prefix}-01",
                title=f"Phân tích mục tiêu: {goal}",
                capability=capability,
                owner="ai_ceo",
                priority=priority,
                acceptance=["Mục tiêu được mô tả rõ", "Rủi ro chính được xác định"],
            ),
            PlannedTask(
                id=f"{prefix}-02",
                title="Lập kế hoạch triển khai theo batch an toàn",
                capability=capability,
                owner="ai_coo",
                priority=priority,
                dependencies=[f"{prefix}-01"],
                acceptance=["Có danh sách task", "Có thứ tự phụ thuộc", "Có tiêu chí nghiệm thu"],
            ),
            PlannedTask(
                id=f"{prefix}-03",
                title="Kiểm tra bảo mật và quyền thực thi",
                capability=capability,
                owner="ai_ciso",
                priority=priority,
                dependencies=[f"{prefix}-02"],
                acceptance=["Không vượt quyền", "Có audit", "Có rollback path"],
            ),
            PlannedTask(
                id=f"{prefix}-04",
                title="Thực thi qua Developer Runtime",
                capability=capability,
                owner="runtime_director",
                priority=priority,
                dependencies=[f"{prefix}-03"],
                acceptance=["Patch preview đạt", "Commit thành công", "Verify đạt"],
            ),
            PlannedTask(
                id=f"{prefix}-05",
                title="Giám sát và báo cáo kết quả về AI CEO",
                capability=capability,
                owner="monitoring_director",
                priority=priority,
                dependencies=[f"{prefix}-04"],
                acceptance=["Có báo cáo sức khỏe", "Có kết luận hoàn thành hoặc lỗi"],
            ),
        ]


task_planner = TaskPlanner()
