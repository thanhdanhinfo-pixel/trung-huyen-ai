from fastapi import APIRouter
from pydantic import BaseModel, Field
import requests
import os
import subprocess
from typing import Dict, Any, Optional

router = APIRouter(
    prefix="/deployment",
    tags=["Deployment"],
)

class RedeployRequest(BaseModel):
    approved: bool = False
    mode: str = "auto"
    reason: Optional[str] = None

def _redeploy_config() -> Dict[str, Any]:
    return {
        "cloud_build_trigger_url_configured": bool(os.getenv("CLOUD_BUILD_TRIGGER_URL")),
        "redeploy_command_configured": bool(os.getenv("REDEPLOY_COMMAND")),
        "service": os.getenv("CLOUD_RUN_SERVICE") or os.getenv("K_SERVICE") or "trung-huyen-ai",
        "region": os.getenv("CLOUD_RUN_REGION") or "asia-southeast1",
    }

@router.post("/smoke-test")
def smoke_test():

    endpoints = [
        "/health",
        "/github/runtime/status",
        "/mcp/ping",
        "/runtime/errors",
        "/version",
        "/rag/init",
    ]

    results = []

    for path in endpoints:

        try:

            response = requests.get(
                f"http://127.0.0.1:8080{path}",
                timeout=10,
            )

            results.append({
                "path": path,
                "status_code": response.status_code,
                "ok": response.ok,
            })

        except Exception as exc:

            results.append({
                "path": path,
                "status_code": None,
                "ok": False,
                "error": str(exc),
                "type": type(exc).__name__,
            })

    overall_ok = all(
        item.get("ok")
        for item in results
    )

    return {
        "status": "ok" if overall_ok else "error",
        "overall_ok": overall_ok,
        "results": results,
    }

@router.post("/rollback")
def rollback():
    try:
        subprocess.run(
            ["git", "revert", "--no-edit", "HEAD"],
            check=True,
        )

        return {
            "status": "ok",
            "message": "Last commit reverted",
        }

    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "type": type(exc).__name__,
        }


@router.get("/capabilities")
def deployment_capabilities():

    return {
        "smoke_test": True,
        "rollback": False,
        "auto_redeploy": False,
        "health_check": True,
        "runtime_error_tracking": True,
    }
