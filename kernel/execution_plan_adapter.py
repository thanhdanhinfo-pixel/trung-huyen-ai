from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from task_queue import Task


@dataclass
class ExecutionPlanAdapter:
    """Convert Planner V2 plans into Runtime Queue tasks.

    Planner produces plans.
    Runtime Queue owns tasks.
    Worker consumes tasks.

    This adapter is the boundary between planning and execution so Worker does
    not depend on Planner internals.
    """

    default_priority: int = 50

    def plan_to_tasks(self, plan: Dict[str, Any]) -> List[Task]:
        if not plan or plan.get("status") not in {"ready", "draft"}:
            return []

        plan_id = plan.get("id")
        goal = plan.get("goal", "")
        tasks: List[Task] = []

        for item in plan.get("tasks", []):
            action = item.get("action", "generic")
            title = item.get("title") or action
            task_goal = f"{goal} :: {title}" if goal else title

            tasks.append(Task(
                goal=task_goal,
                type="execution_plan.task",
                priority=int(item.get("priority", self.default_priority)),
                payload={
                    "plan_id": plan_id,
                    "plan_goal": goal,
                    "task": item,
                    "requires_approval": bool(item.get("requires_approval", True)),
                    "dependencies": item.get("dependencies", []),
                    "source": "planner_v2",
                },
            ))

        return tasks

    def enqueue_plan(self, runtime: Any, plan: Dict[str, Any]) -> Dict[str, Any]:
        tasks = self.plan_to_tasks(plan)
        queued = [runtime.enqueue(task).to_dict() for task in tasks]
        return {
            "status": "ok",
            "plan_id": plan.get("id"),
            "queued_count": len(queued),
            "queued_tasks": queued,
        }


execution_plan_adapter = ExecutionPlanAdapter()
