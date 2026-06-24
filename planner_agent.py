from __future__ import annotations

from typing import Any, Dict, List


class PlannerAgent:
    """Create structured execution-ready plans from high-level goals.

    PlannerAgent does not execute code. It converts a human goal into:
    - plan metadata
    - ordered tasks
    - optional execution_plan tasks that TaskAgent can run through ExecutionEngine
    """

    def create_plan(self, goal: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        context = context or {}
        goal_text = (goal or "").strip()

        if not goal_text:
            return {
                "status": "error",
                "error_type": "ValidationError",
                "message": "goal is required",
            }

        intent = self._classify_goal(goal_text)
        tasks = self._generate_tasks(goal_text, intent=intent, context=context)

        return {
            "status": "ok",
            "goal": goal_text,
            "intent": intent,
            "task_count": len(tasks),
            "tasks": tasks,
            "risks": self._analyze_risks(goal_text, tasks),
        }

    def create_tasks(self, goal: str, context: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        plan = self.create_plan(goal, context=context)
        if plan.get("status") != "ok":
            return []
        return plan.get("tasks", [])

    def _classify_goal(self, goal: str) -> Dict[str, Any]:
        lowered = goal.lower()
        if "kernel" in lowered:
            return {
                "epic": "EPIC-001",
                "name": "ai_kernel_refactor",
                "priority": 10,
                "strategy": "incremental_refactor",
            }
        if "planner" in lowered or "planning" in lowered:
            return {
                "epic": "EPIC-003",
                "name": "planning_engine",
                "priority": 20,
                "strategy": "structured_planning",
            }
        if "worker" in lowered or "agent" in lowered:
            return {
                "epic": "EPIC-004",
                "name": "ai_worker",
                "priority": 15,
                "strategy": "orchestrated_execution",
            }
        return {
            "epic": "EPIC-GENERAL",
            "name": "general_goal",
            "priority": 100,
            "strategy": "manual_review",
        }

    def _generate_tasks(self, goal: str, intent: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        intent_name = intent.get("name")

        if intent_name == "ai_kernel_refactor":
            return self._kernel_tasks(goal, intent)
        if intent_name == "planning_engine":
            return self._planning_tasks(goal, intent)
        if intent_name == "ai_worker":
            return self._worker_tasks(goal, intent)

        return [
            {
                "goal": goal,
                "type": "noop",
                "priority": intent.get("priority", 100),
                "payload": {
                    "reason": "PlannerAgent classified this goal as requiring manual review.",
                    "intent": intent,
                    "context": context,
                },
            }
        ]

    def _kernel_tasks(self, goal: str, intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {
                "goal": "Create AI Kernel foundation files",
                "type": "execution_plan",
                "priority": intent.get("priority", 10),
                "payload": {
                    "approved": False,
                    "plan": {
                        "name": "AI Kernel Foundation",
                        "message": "Add AI Kernel foundation modules",
                        "steps": [
                            {
                                "type": "upsert",
                                "path": "kernel/kernel.py",
                                "content": self._kernel_py_content(),
                            },
                            {
                                "type": "upsert",
                                "path": "kernel/capability.py",
                                "content": self._capability_py_content(),
                            },
                            {
                                "type": "upsert",
                                "path": "kernel/runtime.py",
                                "content": self._runtime_py_content(),
                            },
                        ],
                    },
                },
            }
        ]

    def _planning_tasks(self, goal: str, intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {
                "goal": goal,
                "type": "noop",
                "priority": intent.get("priority", 20),
                "payload": {
                    "message": "Planning Engine already has PlannerAgent foundation. Next step: compiler/validator modules.",
                    "intent": intent,
                },
            }
        ]

    def _worker_tasks(self, goal: str, intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {
                "goal": "Run AI Worker workflow smoke test",
                "type": "noop",
                "priority": intent.get("priority", 15),
                "payload": {
                    "message": "Worker modules are connected through TaskQueue, TaskAgent, WorkflowEngine and AgentOrchestrator.",
                    "intent": intent,
                },
            }
        ]

    def _analyze_risks(self, goal: str, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        risks: List[Dict[str, Any]] = []
        for task in tasks:
            if task.get("type") == "execution_plan" and not task.get("payload", {}).get("approved"):
                risks.append({
                    "level": "medium",
                    "type": "approval_required",
                    "message": "Execution plan requires explicit approval before writing to GitHub.",
                })
        return risks

    def _kernel_py_content(self) -> str:
        return '''from __future__ import annotations\n\nfrom dataclasses import dataclass\n\nfrom kernel.registry import SystemRegistry, load_registry\n\n\n@dataclass\nclass AIKernel:\n    registry: SystemRegistry\n\n    @classmethod\n    def boot(cls) -> "AIKernel":\n        return cls(registry=load_registry())\n\n    def status(self):\n        return {\n            "status": "ok",\n            "registry": self.registry.as_dict(),\n            "registry_validation": self.registry.validate(),\n        }\n\n\nkernel = AIKernel.boot()\n'''

    def _capability_py_content(self) -> str:
        return '''from __future__ import annotations\n\nfrom dataclasses import dataclass\nfrom typing import Dict\n\n\n@dataclass\nclass CapabilityRegistry:\n    capabilities: Dict[str, bool]\n\n    def can(self, capability: str) -> bool:\n        return bool(self.capabilities.get(capability, False))\n\n    def as_dict(self):\n        return dict(self.capabilities)\n\n\ndef default_capabilities() -> CapabilityRegistry:\n    return CapabilityRegistry({\n        "github.read": True,\n        "github.write": True,\n        "drive.read": True,\n        "drive.create": True,\n        "drive.append": True,\n        "mcp.call": True,\n    })\n'''

    def _runtime_py_content(self) -> str:
        return '''from __future__ import annotations\n\nfrom dataclasses import dataclass, field\nfrom datetime import datetime, timezone\nfrom typing import Any, Dict, List\n\n\ndef _now() -> str:\n    return datetime.now(timezone.utc).isoformat()\n\n\n@dataclass\nclass RuntimeState:\n    current_sprint: str = "SPR-001"\n    current_task: str = "AI Worker Foundation"\n    completed_tasks: List[str] = field(default_factory=list)\n    next_actions: List[str] = field(default_factory=list)\n    updated_at: str = field(default_factory=_now)\n\n    def as_dict(self) -> Dict[str, Any]:\n        return {\n            "current_sprint": self.current_sprint,\n            "current_task": self.current_task,\n            "completed_tasks": self.completed_tasks,\n            "next_actions": self.next_actions,\n            "updated_at": self.updated_at,\n        }\n'''
