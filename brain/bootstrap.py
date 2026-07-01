from __future__ import annotations

from brain.facade import living_brain

BOOT_SEQUENCE = [
    'load_constitution',
    'load_governance',
    'load_tool_ownership',
    'initialize_living_brain',
    'bind_capabilities',
    'enable_brain_routing',
]


def bootstrap_brain():
    return {
        'brain_ready': True,
        'brain_owner': 'LIVING_BRAIN',
        'capabilities': living_brain.capabilities(),
        'boot_sequence': BOOT_SEQUENCE,
    }
