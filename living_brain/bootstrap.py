from __future__ import annotations

from pathlib import Path
import yaml
from living_brain.facade import living_brain
from living_brain.tool_router import tool_router, ToolRoutingError


def _load_yaml_if_exists(path: Path):
    if not path.exists():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def bootstrap_brain() -> dict:
    status = {
        "constitution_loaded": False,
        "tool_ownership_loaded": False,
        "brain_initialized": False,
        "brain_routing_enabled": False,
        "delete_capability_loaded": False,
        "deploy_capability_loaded": False,
        "execution_first_loaded": False,
        "capability_baseline_loaded": False,
        "action_contracts_loaded": False,
    }

    constitution = Path("system/GLOBAL_GOVERNANCE/00_SYSTEM_CONSTITUTION.md")
    amendment = Path("system/GLOBAL_GOVERNANCE/00_SYSTEM_CONSTITUTION_APPEND_BRAIN.md")
    ownership = Path("living_brain/tool_ownership.yaml")
    execution_first = Path("governance/EXECUTION_FIRST_PROTOCOL.md")
    capability_baseline = Path("governance/CAPABILITY_BASELINE.yaml")
    action_contracts = Path("governance/ACTION_CONTRACTS.yaml")

    if constitution.exists() and amendment.exists():
        status["constitution_loaded"] = True

    if ownership.exists():
        yaml.safe_load(ownership.read_text(encoding="utf-8"))
        status["tool_ownership_loaded"] = True

    if execution_first.exists():
        status["execution_first_loaded"] = True

    if _load_yaml_if_exists(capability_baseline):
        status["capability_baseline_loaded"] = True

    if _load_yaml_if_exists(action_contracts):
        status["action_contracts_loaded"] = True

    _ = living_brain
    status["brain_initialized"] = True

    try:
        tool_router.resolve("DELETE_CODE")
        status["delete_capability_loaded"] = True

        tool_router.resolve("DEPLOY_SYSTEM")
        status["deploy_capability_loaded"] = True

        status["brain_routing_enabled"] = True
    except ToolRoutingError as exc:
        status["brain_routing_enabled"] = False
        status["routing_error"] = str(exc)

    return status
