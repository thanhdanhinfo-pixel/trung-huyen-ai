from __future__ import annotations

from fastapi import APIRouter

from services.health_service import system_health

try:
    from app import STARTUP_METRICS
except Exception:
    STARTUP_METRICS = {
        "boot": "unknown",
        "scheduler": "unknown",
        "startup_time_ms": None,
    }

router = APIRouter(tags=["system-core"])


def _mcp_loaded() -> bool:
    try:
        from api.mcp import router as mcp_router
        return bool(mcp_router)
    except Exception:
        return False


@router.get("/version")
def version():
    return {
        "system": "TRUNG_HUYEN_AI_OS",
        "version": "1.0.0",
        "ai_brain": "v1",
        "rag": True,
        "qdrant": True,
        "drive": True,
    }


@router.get("/livez")
def livez():
    return {"status": "alive"}


@router.get("/system/startup-metrics")
def startup_metrics():
    return STARTUP_METRICS


@router.get("/readiness")
def readiness():
    payload = system_health()
    payload["mcp_loaded"] = _mcp_loaded()
    payload["ready"] = all(
        [
            payload.get("server") == "ok",
            payload.get("drive", {}).get("status") in {"ok", "degraded"},
            payload.get("openai", {}).get("status") != "missing",
        ]
    )
    return payload


@router.get("/health")
def health():
    payload = system_health()
    payload["mcp_loaded"] = _mcp_loaded()
    return payload


@router.post("/ping-post")
def ping_post():
    return {"status": "ok"}
