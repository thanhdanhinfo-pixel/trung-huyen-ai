from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class PlanTask:
    id: str
    title: str
    action: str
    target: str | None = None
    priority: int = 100
    requires_approval: bool = True
    dependencies: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "action": self.action,
            "target": self.target,
            "priority": self.priority,
            "requires_approval": self.requires_approval,
            "dependencies": self.dependencies,
            "context": self.context,
        }


@dataclass
class Plan:
    id: str
    goal: str
    status: str = "draft"
    created_at: str = field(default_factory=utc_now)
    strategy: str = "awareness_driven"
    tasks: List[PlanTask] = field(default_factory=list)
    risks: List[Dict[str, Any]] = field(default_factory=list)
    awareness: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "goal": self.goal,
            "status": self.status,
            "created_at": self.created_at,
            "strategy": self.strategy,
            "task_count": len(self.tasks),
            "tasks": [task.to_dict() for task in self.tasks],
            "risks": self.risks,
            "awareness": self.awareness,
        }


class PlannerEngine:
    """Awareness-driven planner for AI OS.

    Planner V2 does not generate plans from keywords alone. It observes the
    Kernel, reads SelfState, validates intended actions through Governance and
    uses SystemModel impact data when a target node is supplied.
    """

    def create_plan(
        self,
        kernel: Any,
        goal: str,
        target: str | None = None,
        context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        goal_text = (goal or "").strip()
        if not goal_text:
            return {
                "status": "error",
                "error_type": "ValidationError",
                "message": "goal is required",
            }

        context = context or {}
        awareness = kernel.awareness.summary(kernel)
        self_state = awareness.get("self_state", {})
        tasks = self._build_tasks(
            kernel=kernel,
            goal=goal_text,
            target=target,
            context=context,
            self_state=self_state,
        )
        risks = self._analyze_risks(kernel, tasks, target)

        plan = Plan(
            id=f"plan-{uuid4().hex[:12]}",
            goal=goal_text,
            status="ready" if not any(r.get("level") == "error" for r in risks) else "blocked",
            tasks=tasks,
            risks=risks,
            awareness={
                "observed_at": awareness.get("observed_at"),
                "current_phase": self_state.get("current_phase"),
                "current_sprint": self_state.get("current_sprint"),
                "current_task": self_state.get("current_task"),
                "next_action": self_state.get("next_action"),
                "system_model": awareness.get("system_model", {}),
            },
        )
        return plan.to_dict()

    def plan_next_action(self, kernel: Any) -> Dict[str, Any]:
        awareness = kernel.awareness.summary(kernel)
        self_state = awareness.get("self_state", {})
        next_action = self_state.get("next_action")
        if not next_action:
            return {
                "status": "idle",
                "message": "SelfState has no next action.",
            }
        return self.create_plan(
            kernel=kernel,
            goal=str(next_action),
            context={"source": "self_state.next_action"},
        )

    def _build_tasks(
        self,
        kernel: Any,
        goal: str,
        target: str | None,
        context: Dict[str, Any],
        self_state: Dict[str, Any],
    ) -> List[PlanTask]:
        tasks: List[PlanTask] = []

        inspect_id = "task-001"
        tasks.append(PlanTask(
            id=inspect_id,
            title="Inspect current system state",
            action="system.inspect",
            target=target,
            priority=10,
            requires_approval=False,
            context={
                "goal": goal,
                "phase": self_state.get("current_phase"),
                "sprint": self_state.get("current_sprint"),
            },
        ))

        impact_context: Dict[str, Any] = {}
        if target:
            impact_context = kernel.impact(target)

        tasks.append(PlanTask(
            id="task-002",
            title="Prepare governed implementation plan",
            action="change.prepare",
            target=target,
            priority=20,
            requires_approval=False,
            dependencies=[inspect_id],
            context={
                "goal": goal,
                "impact": impact_context,
                "input": context,
            },
        ))

        tasks.append(PlanTask(
            id="task-003",
            title="Execute approved changes",
            action="change.execute",
            target=target,
            priority=30,
            requires_approval=True,
            dependencies=["task-002"],
            context={
                "goal": goal,
                "governance": "explicit approval required",
            },
        ))

        tasks.append(PlanTask(
            id="task-004",
            title="Verify system and update self state",
            action="system.verify_and_record",
            target=target,
            priority=40,
            requires_approval=False,
            dependencies=["task-003"],
            context={
                "goal": goal,
                "update_self_state": True,
            },
        ))
        return tasks

    def _analyze_risks(
        self,
        kernel: Any,
        tasks: List[PlanTask],
        target: str | None,
    ) -> List[Dict[str, Any]]:
        risks: List[Dict[str, Any]] = []

        for task in tasks:
            validation = kernel.validate_action({
                "type": task.action,
                "target": task.target,
                "requires_approval": task.requires_approval,
            })
            if validation.get("status") in {"blocked", "denied", "error"}:
                risks.append({
                    "level": "error",
                    "type": "governance_block",
                    "task_id": task.id,
                    "details": validation,
                })
            elif task.requires_approval:
                risks.append({
                    "level": "medium",
                    "type": "approval_required",
                    "task_id": task.id,
                    "message": "Execution requires explicit approval.",
                })

        if target and not kernel.find_node(target):
            risks.append({
                "level": "warning",
                "type": "unknown_target",
                "target": target,
                "message": "Target is not present in the current SystemModel.",
            })

        return risks


planner_engine = PlannerEngine()
