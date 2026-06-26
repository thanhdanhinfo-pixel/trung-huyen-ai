from fastapi import APIRouter
import requests
import os
import subprocess

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
