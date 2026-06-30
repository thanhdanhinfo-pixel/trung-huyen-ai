from __future__ import annotations

from fastapi import APIRouter

from config import (
    DRIVE_FOLDER_ID,
    GOOGLE_SERVICE_ACCOUNT_JSON,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    QDRANT_URL,
    QDRANT_API_KEY,
)

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


@router.get("/health")
def health():
    return {
        "server": "ok",
        "version": "1.0.0",
        "google_service_account_json": bool(GOOGLE_SERVICE_ACCOUNT_JSON),
        "drive_folder_id": bool(DRIVE_FOLDER_ID),
        "openai_api_key": bool(OPENAI_API_KEY),
        "openai_model": OPENAI_MODEL,
        "mcp_loaded": _mcp_loaded(),
        "qdrant_url": bool(QDRANT_URL),
        "qdrant_api_key": bool(QDRANT_API_KEY),
    }


@router.post("/ping-post")
def ping_post():
    return {"status": "ok"}
