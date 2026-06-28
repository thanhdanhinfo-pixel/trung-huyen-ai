from typing import Any, Dict


def preflight_context() -> Dict[str, Any]:
    return {
        "status": "READY_TO_EXECUTE",
        "tools": {
            "github_read": True,
            "github_write": True,
            "mcp": True,
            "drive": True,
            "runtime": True,
        },
        "required_sources": [
            "/system/khoi-dong",
            "/system/tool-health",
            "/system/global-memory",
            "/system/last-actions",
            "/system/next-actions",
            "system/CAPABILITY_REGISTRY.yaml",
        ],
        "policy": "OBSERVE_FIRST_VERIFY_CAPABILITIES_CONTINUE_FROM_SYSTEM_STATE",
    }
