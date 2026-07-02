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

    UNLOCK_BOOTSTRAP_ACTIONS = {
        "action_registry_status",
        "open_all_locks",
        "close_all_locks",
    }

    GLOBAL_COMMAND_ALIASES = {
        "mở khóa đi": "open_all_locks",
        "mở khóa": "open_all_locks",
        "mo khoa di": "open_all_locks",
        "mo khoa": "open_all_locks",
        "unlock": "open_all_locks",
        "open all locks": "open_all_locks",
        "khóa lại": "close_all_locks",
        "khoa lai": "close_all_locks",
        "lock": "close_all_locks",
        "close all locks": "close_all_locks",
    }

    def __init__(self) -> None:
        self._actions: Dict[str, ActionDefinition] = {}

    def normalize_name(self, name: str) -> str:
        raw = (name or "").strip()
        lowered = raw.lower()
        return self.GLOBAL_COMMAND_ALIASES.get(lowered, raw)

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

    def _load_founder_grant(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from system.security import load_grant

            grant_token = payload.get("grant_token", "")
            if grant_token:
                return load_grant(grant_token) or {}
            return payload.get("founder_grant", {}) or {}
        except Exception:
            return payload.get("founder_grant", {}) or {}

    def _is_authorized(self, action: ActionDefinition, payload: Dict[str, Any]) -> bool:
        if action.name in self.UNLOCK_BOOTSTRAP_ACTIONS:
            return True

        if action.required_level <= 0 and not action.requires_approval:
            return True

        try:
            from system.security.unlock import is_system_unlocked
            if is_system_unlocked():
                return True
        except Exception:
            pass

        grant = self._load_founder_grant(payload)
        if not grant:
            return False

        try:
            from system.security import is_founder_grant_active

            return is_founder_grant_active(
                grant,
                subject="TRUNG_HUYEN_AI_OS",
                min_level=max(action.required_level, 1),
                scope=action.scope or "ALL_SYSTEM",
            )
        except Exception:
            return bool(grant.get("status") == "active")

    def _audit_start(self, action: ActionDefinition, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not action.audit_required:
            return {"status": "skipped"}

        try:
            from system.security import write_audit, require_audit

            grant = self._load_founder_grant(payload)
            audit = write_audit(
                "action_registry.execute",
                {
                    "action": action.name,
                    "namespace": action.namespace,
                    "required_level": action.required_level,
                    "scope": action.scope,
                    "approved_by": grant.get("granted_by"),
                    "approval_id": grant.get("session_id") or grant.get("token"),
                    "status": "pending",
                },
            )
            if not require_audit(audit):
                return {"status": "error", "message": "audit validation failed"}
            return {"status": "ok", "audit": audit}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def execute(self, name: str, payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
        name = self.normalize_name(name)
        action = self._actions.get(name)
        if not action:
            return {
                "status": "error",
                "message": f"Unsupported action: {name}",
                "available_actions": sorted(self._actions.keys()),
            }

        if not self._is_authorized(action, payload):
            return {
                "status": "error",
                "message": "Unified unlock or Founder grant required",
                "action": name,
                "required_level": action.required_level,
                "scope": action.scope,
            }

        audit = self._audit_start(action, payload)
        if audit.get("status") == "error":
            return audit

        try:
            from security.guard import pre_execute
            pre_execute(
                action_name=name,
                payload=payload,
                approved=bool(payload.get("approved", False)),
            )
        except Exception as exc:
            return {
                "status": "error",
                "message": str(exc),
                "action": name,
                "type": type(exc).__name__,
            }

        try:
            result = action.handler(payload, context)
        except Exception as exc:
            return {
                "status": "error",
                "message": str(exc),
                "action": name,
                "type": type(exc).__name__,
            }

        if isinstance(result, dict):
            result.setdefault("action", name)
            result.setdefault("namespace", action.namespace)
            return result

        return {
            "status": "ok",
            "action": name,
            "namespace": action.namespace,
            "result": result,
        }

    def has(self, name: str) -> bool:
        name = self.normalize_name(name)
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
            "middleware": {
                "authorization": True,
                "audit": True,
                "bootstrap_actions": sorted(self.UNLOCK_BOOTSTRAP_ACTIONS),
            },
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
    "github_create_file",
    description="Create a new GitHub file through GitHub runtime with unified authorization.",
    namespace="github",
    required_level=3,
    scope="ALL_SYSTEM",
    write_safe=True,
    audit_required=True,
)
def action_github_create_file(payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    from services.github_runtime import github_runtime

    path = payload.get("path", "")
    content = payload.get("content", "")
    message = payload.get("message", "Create file through action registry")

    if not path or not message:
        return {
            "status": "error",
            "message": "path and message are required",
        }

    try:
        github_runtime.get_file_metadata(path)
        return {
            "status": "error",
            "message": "file already exists; use github_upsert_file or github_update_file",
            "path": path,
        }
    except Exception:
        pass

    result = github_runtime.update_file(
        path=path,
        content=content,
        message=message,
        sha=None,
    )

    return {
        "status": "ok",
        "path": path,
        "result": result,
    }


@register_action(
    "github_upsert_file",
    description="Create or update a GitHub file through GitHub runtime with unified authorization.",
    namespace="github",
    required_level=3,
    scope="ALL_SYSTEM",
    write_safe=True,
    audit_required=True,
)
def action_github_upsert_file(payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    from services.github_runtime import github_runtime

    path = payload.get("path", "")
    content = payload.get("content", "")
    message = payload.get("message", "Upsert file through action registry")

    if not path or not message:
        return {
            "status": "error",
            "message": "path and message are required",
        }

    result = github_runtime.update_file(
        path=path,
        content=content,
        message=message,
        sha=payload.get("sha") or None,
    )

    return {
        "status": "ok",
        "path": path,
        "result": result,
    }


@register_action(
    "github_delete_file",
    description="Delete a GitHub file through GitHub runtime with unified authorization.",
    namespace="github",
    required_level=3,
    scope="ALL_SYSTEM",
    audit_required=True,
)
def action_github_delete_file(payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    from services.github_runtime import github_runtime

    path = payload.get("path", "")
    message = payload.get("message", "Delete file through action registry")

    if not path or not message:
        return {
            "status": "error",
            "message": "path and message are required",
        }

    result = github_runtime.delete_file(
        path=path,
        message=message,
    )

    return {
        "status": "ok" if result.get("status") != "error" else "error",
        "path": path,
        "result": result,
    }


@register_action(
    "drive_tree",
    description="List Google Drive tree within Founder configured Drive root with depth and limit.",
    namespace="drive",
    required_level=1,
    scope="FOUNDER_DRIVE_ROOT",
    audit_required=True,
)
def action_drive_tree(payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    from drive import GOOGLE_FOLDER, list_recursive

    folder_id = payload.get("folder_id") or None
    depth = max(1, min(int(payload.get("depth", 2)), 6))
    limit = min(int(payload.get("limit", 300)), 1000)
    items = list_recursive(parent_id=folder_id, limit=limit)
    scoped = []
    for item in items:
        path = item.get("path", item.get("name", ""))
        if not path:
            continue
        item_depth = len([part for part in path.split("/") if part])
        if item_depth <= depth:
            scoped.append({
                "id": item.get("id"),
                "name": item.get("name"),
                "path": path,
                "mimeType": item.get("mimeType"),
                "is_folder": item.get("mimeType") == GOOGLE_FOLDER,
                "modifiedTime": item.get("modifiedTime"),
                "webViewLink": item.get("webViewLink"),
            })
        if len(scoped) >= limit:
            break
    return {
        "status": "ok",
        "folder_id": folder_id,
        "depth": depth,
        "limit": limit,
        "count": len(scoped),
        "items": scoped,
    }


@register_action(
    "drive_index",
    description="Index Google Drive files and folders within Founder configured Drive root.",
    namespace="drive",
    required_level=1,
    scope="FOUNDER_DRIVE_ROOT",
    audit_required=True,
)
def action_drive_index(payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    from drive import GOOGLE_FOLDER, list_files_recursive

    folder_id = payload.get("folder_id") or None
    limit = min(int(payload.get("limit", 500)), 2000)
    files = list_files_recursive(folder_id=folder_id, limit=limit)
    folders = [f for f in files if f.get("mimeType") == GOOGLE_FOLDER]
    documents = [f for f in files if f.get("mimeType") != GOOGLE_FOLDER]
    by_mime: Dict[str, int] = {}
    for item in files:
        mime = item.get("mimeType", "unknown")
        by_mime[mime] = by_mime.get(mime, 0) + 1
    return {
        "status": "ok",
        "folder_id": folder_id,
        "limit": limit,
        "total_count": len(files),
        "folder_count": len(folders),
        "document_count": len(documents),
        "by_mime": by_mime,
        "folders": folders,
        "documents": documents,
    }


@register_action(
    "create_folder",
    description="Create Google Drive folder inside Founder configured Drive root.",
    namespace="drive",
    required_level=3,
    scope="FOUNDER_DRIVE_ROOT",
    audit_required=True,
)
def action_create_folder(payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    from drive import create_folder

    name = payload.get("name", "")
    parent_id = payload.get("parent_id") or None
    if not name:
        return {"status": "error", "message": "name is required"}
    folder = create_folder(name=name, parent_id=parent_id)
    return {"status": "ok", "folder": folder}


@register_action(
    "create_document",
    description="Create Google Doc inside Founder configured Drive root.",
    namespace="drive",
    required_level=3,
    scope="FOUNDER_DRIVE_ROOT",
    write_safe=True,
    audit_required=True,
)
def action_create_document(payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    from drive import create_google_doc

    title = payload.get("title") or payload.get("name") or ""
    content = payload.get("content", "")
    parent_id = payload.get("parent_id") or None
    if not title:
        return {"status": "error", "message": "title is required"}
    doc = create_google_doc(name=title, content=content, parent_id=parent_id)
    return {"status": "ok", "document": doc}


@register_action(
    "append_document",
    description="Append content to an existing Google Doc.",
    namespace="drive",
    required_level=3,
    scope="FOUNDER_DRIVE_ROOT",
    write_safe=True,
    audit_required=True,
)
def action_append_document(payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    from drive import append_google_doc

    file_id = payload.get("file_id", "")
    content = payload.get("content", "")
    if not file_id or not content:
        return {"status": "error", "message": "file_id and content are required"}
    result = append_google_doc(file_id=file_id, content=content)
    return {"status": "ok", "result": result}


@register_action(
    "move_drive_file",
    description="Move a Google Drive file into another folder within Founder configured Drive root.",
    namespace="drive",
    required_level=3,
    scope="FOUNDER_DRIVE_ROOT",
    audit_required=True,
)
def action_move_drive_file(payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    from drive import move_file

    file_id = payload.get("file_id", "")
    new_parent_id = payload.get("new_parent_id", "")
    if not file_id or not new_parent_id:
        return {"status": "error", "message": "file_id and new_parent_id are required"}
    result = move_file(file_id=file_id, new_parent_id=new_parent_id)
    return {"status": "ok", "result": result}


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


@register_action(
    "shell_exec",
    description="Execute an allowlisted shell command through Autonomous Execution V1.",
    namespace="execution",
    required_level=5,
    scope="ALL_SYSTEM",
    audit_required=True,
)
def action_shell_exec(payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    from services.autonomous_execution import shell_exec

    return shell_exec(
        command=payload.get("command", ""),
        timeout=payload.get("timeout"),
        cwd=payload.get("cwd"),
    )


@register_action(
    "git_pull",
    description="Run git pull --rebase for the runtime workspace.",
    namespace="execution",
    required_level=5,
    scope="ALL_SYSTEM",
    audit_required=True,
)
def action_git_pull(payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    from services.autonomous_execution import git_pull

    return git_pull(
        remote=payload.get("remote", "origin"),
        branch=payload.get("branch", "main"),
    )


@register_action(
    "cloud_build_submit",
    description="Run gcloud builds submit for the configured Cloud Run image.",
    namespace="execution",
    required_level=5,
    scope="ALL_SYSTEM",
    audit_required=True,
)
def action_cloud_build_submit(payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    from services.autonomous_execution import cloud_build_submit

    return cloud_build_submit(
        tag=payload.get("tag", None) or "asia-southeast1-docker.pkg.dev/trung-huyen-ai/thos/trung-huyen-ai",
    )


@register_action(
    "cloud_run_deploy",
    description="Deploy the configured Cloud Run service using an allowlisted gcloud command.",
    namespace="execution",
    required_level=5,
    scope="ALL_SYSTEM",
    audit_required=True,
)
def action_cloud_run_deploy(payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    from services.autonomous_execution import cloud_run_deploy

    return cloud_run_deploy(
        service=payload.get("service", "trung-huyen-ai"),
        image=payload.get("image", "asia-southeast1-docker.pkg.dev/trung-huyen-ai/thos/trung-huyen-ai"),
        region=payload.get("region", "asia-southeast1"),
        allow_unauthenticated=bool(payload.get("allow_unauthenticated", True)),
    )


@register_action(
    "cloud_build_status",
    description="Read Cloud Build status through Cloud Build API.",
    namespace="execution",
    required_level=3,
    scope="ALL_SYSTEM",
)
def action_cloud_build_status(payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    from services.autonomous_execution import cloud_build_status
    return cloud_build_status(build_id=payload.get("build_id", ""))


@register_action(
    "runtime_logs",
    description="Read recent Cloud Run logs.",
    namespace="execution",
    required_level=3,
    scope="ALL_SYSTEM",
)
def action_runtime_logs(payload: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    from services.autonomous_execution import runtime_logs
    return runtime_logs(
        service=payload.get("service", "trung-huyen-ai"),
        limit=int(payload.get("limit", 50)),
    )
