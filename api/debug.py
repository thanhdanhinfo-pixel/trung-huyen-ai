from fastapi import APIRouter
import os

router = APIRouter(
    prefix="/debug",
    tags=["Debug"]
)


@router.get("/env")
def debug_env():
    mcp_key = os.getenv("MCP_API_KEY", "")

    return {
        "status": "ok",

        "has_mcp_key": bool(mcp_key),
        "mcp_key_length": len(mcp_key),

        "has_openai_key": bool(os.getenv("OPENAI_API_KEY")),

        "has_qdrant_url": bool(os.getenv("QDRANT_URL")),
        "has_qdrant_api_key": bool(os.getenv("QDRANT_API_KEY")),

        "has_google_service_account": bool(
            os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        ),

        "has_drive_folder_id": bool(
            os.getenv("DRIVE_FOLDER_ID")
        ),

        "has_google_client_id": bool(
            os.getenv("GOOGLE_CLIENT_ID")
        ),

        "has_google_client_secret": bool(
            os.getenv("GOOGLE_CLIENT_SECRET")
        ),

        "has_google_refresh_token": bool(
            os.getenv("GOOGLE_REFRESH_TOKEN")
        ),
    }
