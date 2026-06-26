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


@router.post("/redeploy")
def redeploy(req: RedeployRequest):
    if not req.approved:
        return {"status":"error","message":"approved=true is required","config":_redeploy_config()}
    if os.getenv("CLOUD_BUILD_TRIGGER_URL"):
        try:
            r = requests.post(os.getenv("CLOUD_BUILD_TRIGGER_URL"), json={"reason": req.reason or "manual redeploy"}, timeout=30)
            return {"status":"ok" if r.ok else "error","mode":"webhook","status_code":r.status_code,"config":_redeploy_config()}
        except Exception as exc:
            return {"status":"error","message":str(exc),"type":type(exc).__name__}
    if os.getenv("REDEPLOY_COMMAND"):
        try:
            cp = subprocess.run(os.getenv("REDEPLOY_COMMAND"), shell=True, capture_output=True, text=True, timeout=900)
            return {"status":"ok" if cp.returncode==0 else "error","mode":"command","returncode":cp.returncode,"stdout":cp.stdout[-2000:],"stderr":cp.stderr[-2000:]}
        except Exception as exc:
            return {"status":"error","message":str(exc),"type":type(exc).__name__}
    return {"status":"error","message":"Redeploy is not configured","config":_redeploy_config()}

@router.get("/capabilities")
def deployment_capabilities():
    cfg = _redeploy_config()
    return {
        "smoke_test": True,
        "rollback": False,
        "auto_redeploy": cfg["cloud_build_trigger_url_configured"] or cfg["redeploy_command_configured"],
        "redeploy_endpoint": True,
        "health_check": True,
        "runtime_error_tracking": True,
        "config": cfg,
    }
