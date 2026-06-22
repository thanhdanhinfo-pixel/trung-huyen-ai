from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

TaskStatus = Literal["todo","doing","review","done","blocked"]

def utc_now()->str:
    return datetime.now(timezone.utc).isoformat()

@dataclass
class RuntimeTask:
    id:str
    title:str
    worker:str="orchestrator"
    status:TaskStatus="todo"
    priority:int=3
    metadata:Dict[str,Any]=field(default_factory=dict)
    created_at:str=field(default_factory=utc_now)
    updated_at:str=field(default_factory=utc_now)

class AIRuntime:
    def __init__(self):
        self.name="TRUNG_HUYEN_AI_OS Runtime"; self.phase="Foundation"; self.started_at=utc_now(); self.tasks=[]
    def status(self): return {"status":"ok","task_count":len(self.tasks)}
    def add_task(self,title,worker="orchestrator",priority=3,metadata=None):
        t=RuntimeTask(id=f"task-{len(self.tasks)+1:04d}",title=title,worker=worker,priority=priority,metadata=metadata or {})
        self.tasks.append(t); return t.__dict__
    def list_tasks(self): return [t.__dict__ for t in self.tasks]
    def update_task_status(self,task_id,status):
        for t in self.tasks:
            if t.id==task_id:
                t.status=status; t.updated_at=utc_now(); return t.__dict__
        raise ValueError("Task not found")
    def execute(self,title,worker="orchestrator",priority=3,metadata=None):
        task=self.add_task(title,worker,priority,metadata)
        self.update_task_status(task['id'],"doing")
        return {"status":"accepted","task":self.get_task(task['id'])}
    def get_task(self,task_id):
        for t in self.tasks:
            if t.id==task_id:return t.__dict__
        raise ValueError("Task not found")
ai_runtime=AIRuntime()