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
