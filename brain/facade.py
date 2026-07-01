from __future__ import annotations

from typing import Any, Dict
from brain import brain
import yaml
from pathlib import Path

_TOOL_OWNERSHIP = Path(__file__).parent / 'tool_ownership.yaml'


def load_tool_ownership() -> Dict[str, Any]:
    if not _TOOL_OWNERSHIP.exists():
        return {}
    return yaml.safe_load(_TOOL_OWNERSHIP.read_text(encoding='utf-8')) or {}


class LivingBrainFacade:
    def __init__(self):
        self.kernel = brain
        self.ownership = load_tool_ownership()

    def observe(self):
        return self.kernel.self_awareness()

    def plan(self, goal: str, target: str | None = None):
        return self.kernel.plan(goal=goal, target=target)

    def capabilities(self):
        return self.ownership.get('capabilities', {})

    def resolve_tools(self, capability: str):
        return self.capabilities().get(capability, {}).get('tools', [])


living_brain = LivingBrainFacade()
