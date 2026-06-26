from fastapi import APIRouter
import requests

router = APIRouter(prefix="/deployment", tags=["Deployment"])


@router.post("/smoke-test")
def smoke_test():
    endpoints = [
        "/health",
        "/github/runtime/status",
        "/mcp/ping",
        "/runtime/errors",
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

    overall_ok = all(item.get("ok") for item in results)

    return {
        "status": "ok" if overall_ok else "error",
        "overall_ok": overall_ok,
        "results": results,
    }


@router.post("/rollback")
def rollback():
    return {
        "status": "not_implemented",
        "message": "Future capability: revert last commit and redeploy."
    }
