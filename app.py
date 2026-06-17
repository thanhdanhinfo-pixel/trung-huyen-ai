from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from config import DRIVE_FOLDER_ID, GOOGLE_SERVICE_ACCOUNT_JSON, OPENAI_API_KEY
from drive import list_files, search_files

app = FastAPI(
    title="Trung Huyen AI Server",
    version="1.0.0",
    description="AI server nền tảng kết nối Google Drive cho Trung Huyền Academy.",
)


@app.get("/")
def root():
    return {
        "name": "TRUNG_HUYEN_AI_SERVER",
        "status": "running",
        "message": "Server đã chạy. Bước tiếp theo: cấu hình GOOGLE_SERVICE_ACCOUNT_JSON trên Render.",
    }


@app.get("/health")
def health():
    return {
        "server": "ok",
        "google_service_account_json": bool(GOOGLE_SERVICE_ACCOUNT_JSON),
        "drive_folder_id": bool(DRIVE_FOLDER_ID),
        "openai_api_key": bool(OPENAI_API_KEY),
    }


@app.get("/drive/files")
def drive_files(limit: int = Query(default=50, ge=1, le=200)):
    try:
        return {
            "status": "ok",
            "folder_limited": bool(DRIVE_FOLDER_ID),
            "files": list_files(limit=limit),
        }
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(exc),
            },
        )


@app.get("/drive/search")
def drive_search(q: str = Query(..., min_length=1), limit: int = Query(default=20, ge=1, le=100)):
    try:
        return {
            "status": "ok",
            "query": q,
            "files": search_files(q=q, limit=limit),
        }
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(exc),
            },
        )
