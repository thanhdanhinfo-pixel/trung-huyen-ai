from __future__ import annotations

from typing import Any, Dict
from kernel.kernel import kernel as neural_core
import yaml
from pathlib import Path

_TOOL_OWNERSHIP = Path(__file__).parent / 'tool_ownership.yaml'


def load_tool_ownership() -> Dict[str, Any]:
    if not _TOOL_OWNERSHIP.exists():
        return {}
    return yaml.safe_load(_TOOL_OWNERSHIP.read_text(encoding='utf-8')) or {}


class LivingBrainFacade:
    NAME = 'LIVING_BRAIN'
    ROLE = 'CONTROL_PLANE'
    VERSION = '1.0'

    def __init__(self):
        self.neural_core = neural_core
        self.ownership = load_tool_ownership()

    def observe(self):
        return self.neural_core.self_awareness()

    def plan(self, goal: str, target: str | None = None):
        return self.neural_core.plan(goal=goal, target=target)

    def capabilities(self):
        return self.ownership.get('capabilities', {})

    def resolve_tools(self, capability: str):
        return self.capabilities().get(capability, {}).get('tools', [])


living_brain = LivingBrainFacade()
