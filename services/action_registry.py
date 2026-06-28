from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Callable, Dict, List, Optional

ActionHandler = Callable[[Dict[str, Any], Any], Dict[str, Any]]


@dataclass
class ActionDefinition:
    name: str
    handler: ActionHandler
    description: str = ""
    requires_approval: bool = False
    namespace: str = "default"
    required_level: int = 0
    scope: str = ""
    write_safe: bool = False
    audit_required: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data.pop("handler", None)
        return data


class ActionRegistry:
    """Central registry for runtime actions.

    Runtime capabilities should be registered here instead of being scattered
    across routers or long if/else blocks.
    """

    def __init__(self) -> None:
        self._actions: Dict[str, ActionDefinition] = {}

    def register(
        self,
        name: str,
        handler: ActionHandler,
        description: str = "",
        requires_approval: bool = False,
        namespace: Optional[str] = None,
        required_level: int = 0,
        scope: str = "",
        write_safe: bool = False,
        audit_required: bool = False,
    ) -> None:
        self._actions[name] = ActionDefinition(
            name=name,
            handler=handler,
            description=description,
            requires_approval=requires_approval,
            namespace=namespace or name.split(".", 1)[0],
            required_level=required_level,
            scope=scope,
            write_safe=write_safe,
            audit_required=audit_required,
        )

    def action(self, name: str, **metadata):
        def decorator(func: ActionHandler):
            self.register(name=name, handler=func, **metadata)
            return func
        return decorator

    def get(self, name: str) -> Optional[ActionDefinition]:
        return self._actions.get(name)

    def execute(self, name: str, payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
        action = self._actions.get(name)
        if not action:
            return {
                "status": "error",
                "message": f"Unsupported action: {name}",
                "available_actions": sorted(self._actions.keys()),
            }
        return action.handler(payload, context)

    def has(self, name: str) -> bool:
        return name in self._actions

    def list_actions(self) -> List[Dict[str, Any]]:
        return [self._actions[key].to_dict() for key in sorted(self._actions.keys())]

    def status(self) -> Dict[str, Any]:
        by_namespace: Dict[str, int] = {}
        for action in self._actions.values():
            by_namespace[action.namespace] = by_namespace.get(action.namespace, 0) + 1
        return {
            "status": "ok",
            "action_count": len(self._actions),
            "namespaces": by_namespace,
            "actions": sorted(self._actions.keys()),
        }


action_registry = ActionRegistry()
register_action = action_registry.action


@register_action(
    "action_registry_status",
    description="Return Action Registry status and registered actions.",
    namespace="system",
)
def action_registry_status(payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    return action_registry.status()


@register_action(
    "open_all_locks",
    description="RULE-019 unified unlock command. Opens all registered lock layers.",
    namespace="security",
    required_level=5,
    scope="ALL_SYSTEM",
    audit_required=True,
)
def action_open_all_locks(payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    from system.security.unlock import open_all_locks

    return open_all_locks(
        reason=payload.get("reason", "Founder command"),
    )


@register_action(
    "close_all_locks",
    description="Close unified unlock state and relock the system.",
    namespace="security",
    required_level=5,
    scope="ALL_SYSTEM",
    audit_required=True,
)
def action_close_all_locks(payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    from system.security.unlock import close_all_locks

    return close_all_locks(
        reason=payload.get("reason", "Founder command"),
    )


@register_action(
    "github_update_file",
    description="Update a GitHub file through system_write and WRITE_SAFETY_GATE.",
    namespace="github",
    required_level=3,
    scope="ALL_SYSTEM",
    write_safe=True,
    audit_required=True,
)
def action_github_update_file(payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    from system.security import load_grant, system_write

    grant_token = payload.get("grant_token", "")
    grant = load_grant(grant_token) if grant_token else payload.get("founder_grant", {})

    path = payload.get("path", "")
    content = payload.get("content", "")
    sha = payload.get("sha", "")
    message = payload.get("message", "")

    if not path or not content or not message:
        return {
            "status": "error",
            "message": "path, content and message are required",
        }

    result = system_write(
        action="update_file",
        target=path,
        payload={
            "content": content,
            "message": message,
            "sha": sha,
        },
        founder_grant=grant or {},
    )

    return {
        "status": "ok" if result.get("status") != "error" else "error",
        "result": result,
    }


@register_action(
    "patch_file",
    description="Patch a GitHub file through system_write and WRITE_SAFETY_GATE.",
    namespace="github",
    required_level=3,
    scope="ALL_SYSTEM",
    write_safe=True,
    audit_required=True,
)
def action_patch_file(payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    from system.security import load_grant, system_write

    grant_token = payload.get("grant_token", "")
    grant = load_grant(grant_token) if grant_token else payload.get("founder_grant", {})

    path = payload.get("path", "")
    find = payload.get("find", "")
    replace = payload.get("replace", "")
    message = payload.get("message", "system write patch")

    if not path or not find:
        return {
            "status": "error",
            "message": "path and find are required",
        }

    result = system_write(
        action="patch_file",
        target=path,
        payload={
            "find": find,
            "replace": replace,
            "message": message,
        },
        founder_grant=grant or {},
    )

    return {
        "status": "ok" if result.get("status") != "error" else "error",
        "result": result,
    }


@register_action(
    "move_file",
    description="Move a GitHub file through system_write.",
    namespace="github",
    required_level=3,
    scope="ALL_SYSTEM",
    audit_required=True,
)
def action_move_file(payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    from system.security import load_grant, system_write

    grant_token = payload.get("grant_token", "")
    grant = load_grant(grant_token) if grant_token else payload.get("founder_grant", {})

    source = payload.get("source") or payload.get("path") or ""
    destination = payload.get("destination", "")
    message = payload.get("message", "system write move")

    if not source or not destination:
        return {
            "status": "error",
            "message": "source/path and destination are required",
        }

    result = system_write(
        action="move_file",
        target=source,
        payload={
            "destination": destination,
            "message": message,
        },
        founder_grant=grant or {},
    )

    return {
        "status": "ok" if result.get("status") != "error" else "error",
        "result": result,
    }


@register_action(
    "developer.execute",
    description="Submit a developer workflow action through the unified action registry.",
    namespace="developer",
    required_level=5,
    scope="ALL_SYSTEM",
    audit_required=True,
)
def action_developer_execute(payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    from services.workflow_engine import workflow_engine
    from system.security.unlock import is_system_unlocked
    from system.security import load_grant

    grant_token = payload.get("grant_token", "")
    grant = load_grant(grant_token) if grant_token else payload.get("founder_grant", {})

    if not (is_system_unlocked() or grant):
        return {
            "status": "error",
            "message": "Unified unlock or Founder grant required",
        }

    action = payload.get("action", "")
    action_payload = payload.get("payload", {})
    requires_approval = bool(payload.get("requires_approval", False))
    auto_run = bool(payload.get("auto_run", True))

    if not action:
        return {
            "status": "error",
            "message": "action is required",
        }

    return workflow_engine.submit(
        action=f"developer.{action}",
        payload=action_payload,
        requires_approval=requires_approval,
        auto_run=auto_run,
    )


@register_action(
    "execute_plan",
    description="Execute an approved execution plan through the unified action registry.",
    namespace="execution",
    required_level=3,
    scope="ALL_SYSTEM",
    audit_required=True,
)
def action_execute_plan(payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    from services.execution_engine import execution_engine, execution_plan_from_dict
    from system.security.unlock import is_system_unlocked
    from system.security import load_grant

    grant_token = payload.get("grant_token", "")
    grant = load_grant(grant_token) if grant_token else payload.get("founder_grant", {})

    approved = bool(is_system_unlocked() or grant)
    if not approved:
        return {
            "status": "error",
            "message": "Unified unlock or Founder grant required",
        }

    plan_data = payload.get("plan") or {}
    if not isinstance(plan_data, dict):
        return {
            "status": "error",
            "message": "plan must be an object",
        }

    plan = execution_plan_from_dict(plan_data)
    result = execution_engine.execute(
        plan=plan,
        approved=True,
    )

    return {
        "status": result.get("status"),
        "result": result,
    }
