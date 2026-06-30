from __future__ import annotations

from config import (
    DRIVE_FOLDER_ID,
    GOOGLE_SERVICE_ACCOUNT_JSON,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    QDRANT_API_KEY,
    QDRANT_URL,
)


def system_health() -> dict:
    return {
        "server": "ok",
        "version": "1.0.0",
        "drive": {
            "status": "ok" if DRIVE_FOLDER_ID and GOOGLE_SERVICE_ACCOUNT_JSON else "degraded",
        },
        "openai": {
            "status": "configured" if OPENAI_API_KEY else "missing",
            "model": OPENAI_MODEL,
        },
        "qdrant": {
            "status": "configured" if QDRANT_URL else "missing",
            "api_key": bool(QDRANT_API_KEY),
        },
    }
