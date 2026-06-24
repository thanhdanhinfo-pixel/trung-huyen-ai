from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ArchitectureDecision:
    id: str
    title: str
    decision: str
    reason: str = ""
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "decision": self.decision,
            "reason": self.reason,
            "created_at": self.created_at,
        }


@dataclass
class SelfState:
    """Operational self-awareness state for AI Kernel.

    Memory stores long-term knowledge.
    Runtime stores execution state.
    SelfState stores development/navigation state: where the AI OS is in its
    own restructuring roadmap and what it should do next.
    """

    current_phase: str = "System Awareness"
    current_epic: str = "SA-4 Self Awareness"
    current_sprint: str = "SA-4.1 Self State"
    current_task: str = "Create Kernel SelfState foundation"
    objective: str = "Build an AI OS that understands, operates and evolves its own system."
    architecture_version: str = "AI_OS_V2_KERNEL_AWARENESS"
    progress: Dict[str, Any] = field(default_factory=lambda: {
        "kernel_foundation": "complete",
        "system_awareness": "mostly_complete",
        "runtime_awareness": "in_progress",
        "self_awareness": "in_progress",
        "planner_v2": "not_started",
    })
    last_commit: str | None = None
    last_refresh: str | None = None
    next_action: str = "Integrate SelfState into AwarenessManager"
    decisions: List[ArchitectureDecision] = field(default_factory=list)
    updated_at: str = field(default_factory=utc_now)

    def update_task(self, task: str, next_action: str | None = None) -> None:
        self.current_task = task
        if next_action is not None:
            self.next_action = next_action
        self.updated_at = utc_now()

    def update_commit(self, commit_sha: str) -> None:
        self.last_commit = commit_sha
        self.updated_at = utc_now()

    def mark_refresh(self) -> None:
        self.last_refresh = utc_now()
        self.updated_at = utc_now()

    def add_decision(self, decision: ArchitectureDecision) -> None:
        self.decisions.append(decision)
        self.updated_at = utc_now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_phase": self.current_phase,
            "current_epic": self.current_epic,
            "current_sprint": self.current_sprint,
            "current_task": self.current_task,
            "objective": self.objective,
            "architecture_version": self.architecture_version,
            "progress": self.progress,
            "last_commit": self.last_commit,
            "last_refresh": self.last_refresh,
            "next_action": self.next_action,
            "decisions": [decision.to_dict() for decision in self.decisions],
            "updated_at": self.updated_at,
        }


def load_self_state() -> SelfState:
    state = SelfState()
    state.add_decision(ArchitectureDecision(
        id="ADR-001",
        title="Kernel-first architecture",
        decision="AIKernel is the single coordination root for identity, runtime, governance, memory, system model and awareness.",
        reason="Prevents agents and workers from owning duplicated system state.",
    ))
    state.add_decision(ArchitectureDecision(
        id="ADR-002",
        title="Digital Twin for System Awareness",
        decision="SystemModel represents the AI OS as nodes and relationships.",
        reason="AI must reason over an internal model of the system instead of guessing from files.",
    ))
    state.add_decision(ArchitectureDecision(
        id="ADR-003",
        title="AwarenessManager aggregation",
        decision="Observers are aggregated through AwarenessManager instead of being scattered across AIKernel.",
        reason="Keeps AIKernel from becoming a God Object and allows future observers to be added safely.",
    ))
    return state


self_state = load_self_state()
