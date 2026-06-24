from __future__ import annotations

from typing import Any, Dict, List, Optional

from task_agent import TaskAgent
from task_queue import Task, TaskQueue


class WorkflowEngine:
    """Run tasks through TaskQueue and TaskAgent.

    WorkflowEngine is responsible for the execution lifecycle:
    - enqueue tasks
    - pop next task
    - execute with TaskAgent
    - mark complete or failed/retry in TaskQueue
    - return a structured workflow report
    """

    def __init__(self, queue: Optional[TaskQueue] = None, agent: Optional[TaskAgent] = None):
        self.queue = queue or TaskQueue()
        self.agent = agent or TaskAgent()

    def enqueue(self, task: Task | Dict[str, Any]) -> Task:
        return self.queue.push(task)

    def run_once(self) -> Dict[str, Any]:
        task = self.queue.pop()
        if not task:
            return {
                "status": "idle",
                "message": "No pending task.",
                "queue": self.queue.snapshot(),
            }

        task_data = task.to_dict()
        result = self.agent.execute(task_data)
        result_status = result.get("status")

        if result_status in {"ok", "completed", "success"}:
            completed = self.queue.complete(task, result=result)
            return {
                "status": "completed",
                "task": completed.to_dict(),
                "result": result,
                "queue": self.queue.snapshot(),
            }

        failed = self.queue.fail(
            task,
            error={
                "status": result_status or "error",
                "error_type": result.get("error_type", "TaskExecutionError"),
                "message": result.get("message", "Task execution failed."),
                "result": result,
            },
        )

        return {
            "status": "retrying" if failed.status.value == "pending" else "failed",
            "task": failed.to_dict(),
            "result": result,
            "queue": self.queue.snapshot(),
        }

    def run(self, tasks: Optional[List[Task | Dict[str, Any]]] = None, max_steps: int = 100) -> Dict[str, Any]:
        if tasks:
            for task in tasks:
                self.enqueue(task)

        events: List[Dict[str, Any]] = []
        steps = 0

        while steps < max_steps:
            event = self.run_once()
            events.append(event)
            steps += 1

            if event.get("status") == "idle":
                break

        return {
            "status": "ok",
            "steps": steps,
            "events": events,
            "queue": self.queue.snapshot(),
        }
