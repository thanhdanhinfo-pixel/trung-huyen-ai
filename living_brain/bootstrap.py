from __future__ import annotations

from pathlib import Path
import yaml
from living_brain.facade import living_brain
from living_brain.tool_router import tool_router, ToolRoutingError


def bootstrap_brain() -> dict:
    status = {
        "constitution_loaded": False,
        "tool_ownership_loaded": False,
        "brain_initialized": False,
        "brain_routing_enabled": False,
        "delete_capability_loaded": False,
        "deploy_capability_loaded": False,
    }

    constitution = Path("system/GLOBAL_GOVERNANCE/00_SYSTEM_CONSTITUTION.md")
    amendment = Path("system/GLOBAL_GOVERNANCE/00_SYSTEM_CONSTITUTION_APPEND_BRAIN.md")
    ownership = Path("living_brain/tool_ownership.yaml")

    if constitution.exists() and amendment.exists():
        status["constitution_loaded"] = True

    if ownership.exists():
        yaml.safe_load(ownership.read_text(encoding="utf-8"))
        status["tool_ownership_loaded"] = True

    _ = living_brain
    status["brain_initialized"] = True
    status["brain_routing_enabled"] = True
    return status
