from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from task_agent import TaskAgent
from task_queue import TaskQueue
from workflow_engine import WorkflowEngine


class AgentStatus(str, Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"


@dataclass
class AgentRecord:
    name: str
    agent: Any
    task_types: List[str] = field(default_factory=list)
    status: AgentStatus = AgentStatus.IDLE
    last_result: Optional[Dict[str, Any]] = None
    last_error: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "task_types": self.task_types,
            "status": self.status.value,
            "last_result": self.last_result,
            "last_error": self.last_error,
        }


class AgentOrchestrator:
    """Coordinate agents and route tasks to workflow execution.

    The orchestrator keeps the public `register` and `list_agents` behavior,
    but now adds:
    - task type routing
    - agent status tracking
    - structured workflow execution
    - single-task and batch-task execution helpers
    """

    def __init__(self):
        self.agents: Dict[str, AgentRecord] = {}
        self.default_queue = TaskQueue()
        self.default_agent = TaskAgent()
        self.workflow = WorkflowEngine(queue=self.default_queue, agent=self.default_agent)
        self.register("default_task_agent", self.default_agent, task_types=["noop", "execution_plan", "generic"])

    def register(self, name: str, agent: Any, task_types: Optional[List[str]] = None):
        self.agents[name] = AgentRecord(
            name=name,
            agent=agent,
            task_types=task_types or [],
        )
        return self.agents[name].to_dict()

    def list_agents(self):
        return list(self.agents.keys())

    def describe_agents(self) -> List[Dict[str, Any]]:
        return [record.to_dict() for record in self.agents.values()]

    def find_agent(self, task_type: str) -> Optional[AgentRecord]:
        for record in self.agents.values():
            if task_type in record.task_types:
                return record
        return self.agents.get("default_task_agent")

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("type", "generic")
        record = self.find_agent(task_type)

        if not record:
            return {
                "status": "error",
                "error_type": "NoAgentAvailable",
                "message": f"No agent available for task type: {task_type}",
                "task": task,
            }

        record.status = AgentStatus.BUSY
        try:
            workflow = WorkflowEngine(queue=TaskQueue(), agent=record.agent)
            result = workflow.run(tasks=[task], max_steps=10)
            record.status = AgentStatus.IDLE
            record.last_result = result
            record.last_error = None
            return {
                "status": "ok",
                "agent": record.name,
                "task_type": task_type,
                "result": result,
            }
        except Exception as exc:
            error = {
                "error_type": type(exc).__name__,
                "message": str(exc),
            }
            record.status = AgentStatus.ERROR
            record.last_error = error
            return {
                "status": "error",
                "agent": record.name,
                "task_type": task_type,
                "error": error,
                "task": task,
            }

    def run_workflow(self, tasks: List[Dict[str, Any]], max_steps: int = 100) -> Dict[str, Any]:
        events: List[Dict[str, Any]] = []
        for task in tasks:
            events.append(self.execute_task(task))
            if len(events) >= max_steps:
                break

        failed = [event for event in events if event.get("status") != "ok"]
        return {
            "status": "ok" if not failed else "partial_error",
            "total": len(tasks),
            "executed": len(events),
            "failed": len(failed),
            "events": events,
            "agents": self.describe_agents(),
        }
