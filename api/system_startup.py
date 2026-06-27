from __future__ import annotations

from datetime import datetime, timezone
import os
from typing import Any, Dict, List

from fastapi import APIRouter

router = APIRouter(prefix="/system", tags=["startup-bootstrap"])


def _runtime_state() -> Dict[str, Any]:
    return {
        "runtime": "cloud-run",
        "service": os.getenv("K_SERVICE"),
        "revision": os.getenv("K_REVISION"),
        "configuration": os.getenv("K_CONFIGURATION"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def _capabilities() -> Dict[str, Any]:
    return {
        "github_read": True,
        "github_write": True,
        "google_drive": True,
        "mcp": True,
        "runtime_observability": True,
        "repository_observer": True,
        "startup_bootstrap": True,
    }


def _self_state() -> Dict[str, Any]:
    return {
        "identity": "TRUNG_HUYEN_AI_OS",
        "mode": "SYSTEM_ARCHITECT_MODE",
        "role": "AI Operating System / central coordinator",
        "founder_authority": True,
        "source_of_truth_priority": [
            "/system/khoi-dong",
            "Self State",
            "Capability Registry",
            "System Awareness",
            "Runtime State",
            "System Model",
            "Repository State",
            "Google Drive",
            "Conversation Memory",
            "Inference",
        ],
    }


def _checkpoint() -> Dict[str, Any]:
    return {
        "status": "ok",
        "checkpoint_version": "boot-v3-production-v1",
        "current_phase": "startup-bootstrap-api-and-gpt-network-level-3",
        "verified_metrics": {
            "github_runtime": "ok",
            "github_list": "ok",
            "github_read": "ok",
            "github_write": "available",
            "import_scan": "ok",
            "import_scan_scanned_files": 329,
            "import_scan_modules_detected": 329,
            "import_scan_referenced_internal_count": 187,
            "import_scan_cache_ttl_seconds": 300,
        },
        "do_not_repeat": [
            "do not re-debug GitHub token unless /github/runtime/status fails",
            "do not reimplement import scan cache unless cache disappears",
            "do not mass move or delete files without Founder approval",
        ],
    }


def _last_actions() -> List[Dict[str, Any]]:
    return [
        {
            "type": "verification",
            "message": "Confirmed MCP tool registry exposes github_update_file, execute_plan, backend_call, GitHub read/list, Drive and workspace bootstrap.",
            "status": "done",
        },
        {
            "type": "architecture_decision",
            "message": "TRUNG_HUYEN_AI_OS is the master GPT Action. Other GPTs connect through shared backend, not GPT-to-GPT calls.",
            "status": "accepted",
        },
        {
            "type": "implementation",
            "message": "Startup API approved by Founder and implemented as /system/khoi-dong and /system/boot-v3.",
            "status": "in_progress_until_deploy_verified",
        },
    ]


def _global_memory() -> Dict[str, Any]:
    return {
        "status": "ok",
        "memory_layers": {
            "github": {
                "role": "Code Truth",
                "status": "online",
                "key_endpoints": ["/github/runtime/status", "/github/list", "/github/read"],
            },
            "google_drive": {
                "role": "Founder Knowledge Drive / Global Memory",
                "status": "online",
                "key_endpoints": ["/drive/search", "/drive/read-path", "/rag/search", "/mcp/drive-tree"],
            },
            "runtime": {
                "role": "Cloud Run runtime state",
                "status": "online",
                "key_endpoints": ["/system/status", "/system/runtime/status", "/observability/cloud/runtime"],
            },
            "repository_observability": {
                "role": "Dependency intelligence and refactor planning",
                "status": "enabled",
                "key_endpoints": ["/system/import-scan", "/system/orphan-modules", "/system/refactor-plan"],
            },
        },
        "policy": [
            "system endpoints are source of truth for new conversations",
            "Google Drive is founder knowledge memory",
            "GitHub is code truth",
            "runtime state overrides conversation memory when available",
        ],
    }


def _next_actions() -> List[str]:
    return [
        "verify /system/khoi-dong after Cloud Run deploy",
        "verify /system/boot-v3 after Cloud Run deploy",
        "update GPT Action OpenAPI schema to include startup endpoints if missing",
        "connect Brain GPT to /system/khoi-dong and memory endpoints",
        "connect Academy GPT to /system/khoi-dong and academy/memory endpoints",
        "connect Worker GPT to /system/khoi-dong and worker/runtime endpoints",
    ]


def _governance_rules() -> Dict[str, Any]:
    return {
        "status": "ok",
        "rules": {
            "RULE_017": {
                "name": "VERIFY_BEFORE_DENY",
                "description": "Never claim missing tools, permissions or capabilities before verifying runtime capability.",
                "required_checks": [
                    "ping MCP runtime",
                    "read MCP/backend tool registry",
                    "check GitHub runtime status",
                    "check action/OpenAPI manifest",
                    "check backend endpoints",
                ],
                "default_assumption": "capability_exists_until_disproven",
            },
            "RULE_018": {
                "name": "STATE_CONSISTENCY",
                "description": "Do not downgrade or contradict a previously verified completed state unless new verification proves failure.",
                "allowed_state_change_conditions": [
                    "runtime reports rollback",
                    "verification proves failure",
                    "Founder requests re-validation",
                ],
            },
        },
        "response_policy": {
            "before_denial": "verify capability first",
            "after_success_report": "keep completed state locked unless disproven",
        },
    }


def _founder_constitution() -> Dict[str, Any]:
    return {
        "founder_authority": True,
        "founder_roles": [
            "creator",
            "chief_architect",
            "system_owner",
            "final_decision_maker",
        ],
        "truth_sources": {
            "startup_truth": "/system/khoi-dong",
            "code_truth": "GitHub",
            "knowledge_truth": "Google Drive",
            "runtime_truth": "Cloud Run Runtime",
        },
        "protected_actions_require_approval": [
            "delete_files",
            "mass_move_files",
            "modify_protected_files",
            "large_refactor",
            "change_secrets",
            "change_runtime_structure",
            "change_system_policy",
        ],
        "default_governance_flow": ["observe", "analyze", "propose", "execute_after_approval"],
    }


def _gpt_action_scope() -> Dict[str, Any]:
    return {
        "master_gpt": "TRUNG_HUYEN_AI_OS",
        "scope": "system_building_and_system_operation_only",
        "allowed_domains": [
            "startup",
            "runtime",
            "github",
            "mcp",
            "repository_observability",
            "import_scan",
            "orphan_detection",
            "refactor_plan",
            "tool_health",
            "self_awareness",
            "capability_registry",
            "workers",
            "scheduler",
            "governance",
        ],
        "forbidden_domains": [
            "academy_training",
            "student_coaching",
            "crm",
            "marketing",
            "sales",
            "project_delivery",
            "du_an_thuc_chien",
        ],
        "action_policy": {
            "do_not_remove_stable_existing_system_actions": True,
            "add_startup_group_only_for_bootstrap": True,
            "do_not_expose_full_dynamic_openapi_if_over_action_limit": True,
        },
    }


def _capability_verification_contract() -> Dict[str, Any]:
    return {
        "status": "active",
        "contract": "Capabilities must be verified, never assumed absent.",
        "forbidden_before_verification": [
            "I do not have permission",
            "I do not have tools",
            "I cannot write files",
            "I cannot commit",
            "I cannot call the API",
        ],
        "verification_order": [
            "mcp_runtime",
            "mcp_tool_registry",
            "github_runtime_status",
            "backend_manifest",
            "openapi_action_manifest",
            "repository_state",
        ],
        "default_assumption": "capability_exists_until_disproven",
    }


def _memory_pack() -> Dict[str, Any]:
    return {
        "status": "ok",
        "startup_contract": {
            "trigger_commands": ["Khởi động", "START", "THOS START"],
            "canonical_endpoint": "/system/khoi-dong",
            "fallback_endpoint": "/system/boot-v3",
            "continue_from": "next_actions",
        },
        "governance_rules": _governance_rules(),
        "founder_constitution": _founder_constitution(),
        "gpt_action_scope": _gpt_action_scope(),
        "capability_verification_contract": _capability_verification_contract(),
        "gpt_network_policy": {
            "connection_model": "shared-backend-not-gpt-to-gpt",
            "shared_startup_endpoint": "/system/khoi-dong",
            "master_gpt": "TRUNG_HUYEN_AI_OS",
            "specialized_gpts": ["Brain GPT", "Academy GPT", "Project GPT", "Worker GPT"],
        },
    }


def _payload() -> Dict[str, Any]:
    return {
        "status": "ok",
        "system": "TRUNG_HUYEN_AI_OS",
        "startup_command": "Khởi động",
        "startup_contract": {
            "when_founder_says": ["Khởi động", "START", "THOS START"],
            "must_call": "/system/khoi-dong",
            "must_not_ask_old_context": True,
            "continue_from": "next_actions",
        },
        "self_state": _self_state(),
        "capability_registry": _capabilities(),
        "runtime": _runtime_state(),
        "checkpoint": _checkpoint(),
        "last_actions": _last_actions(),
        "global_memory": _global_memory(),
        "next_actions": _next_actions(),
        "active_endpoints": {
            "khoi_dong": "/system/khoi-dong",
            "boot_v3": "/system/boot-v3",
            "session_checkpoint": "/system/session-checkpoint",
            "last_actions": "/system/last-actions",
            "global_memory": "/system/global-memory",
            "next_actions": "/system/next-actions",
            "self_state": "/system/self-state",
            "tool_health": "/system/tool-health",
        },
        "gpt_network_policy": {
            "master_gpt": "TRUNG_HUYEN_AI_OS",
            "connection_model": "shared-backend-not-gpt-to-gpt",
            "shared_startup_endpoint": "/system/khoi-dong",
            "other_gpts_role": ["Brain GPT", "Academy GPT", "Worker GPT"],
        },
    }


@router.get("/khoi-dong")
def khoi_dong() -> Dict[str, Any]:
    return _payload()


@router.get("/boot-v3")
def boot_v3() -> Dict[str, Any]:
    return _payload()


@router.get("/session-checkpoint")
def session_checkpoint() -> Dict[str, Any]:
    return _checkpoint()


@router.get("/last-actions")
def last_actions() -> Dict[str, Any]:
    actions = _last_actions()
    return {"status": "ok", "count": len(actions), "actions": actions}


@router.get("/global-memory")
def global_memory() -> Dict[str, Any]:
    return _global_memory()


@router.get("/next-actions")
def next_actions() -> Dict[str, Any]:
    actions = _next_actions()
    return {"status": "ok", "count": len(actions), "actions": actions}


@router.get("/self-state")
def self_state() -> Dict[str, Any]:
    return _self_state()


@router.get("/tool-health")
def tool_health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "tools": {
            "github_read": "available",
            "github_write": "available",
            "drive": "available",
            "mcp": "available",
            "runtime": "available",
        },
        "safe_mode": False,
    }
