from typing import Any, Dict, List

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel, Field
from fastapi import Request

from config import (
    DRIVE_FOLDER_ID,
    GOOGLE_SERVICE_ACCOUNT_JSON,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    MAX_CONTEXT_CHARS,
)
from drive import list_files, search_files, read_file_content, search_and_read


SERVER_URL = "https://trung-huyen-ai-779121307308.asia-southeast1.run.app"

app = FastAPI(
    title="TRUNG_HUYEN_AI_OS",
    version="1.0.0",
    description="Bộ não AI kết nối Google Drive và OpenAI cho Trung Huyền Academy.",
    servers=[{"url": SERVER_URL}],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


try:
    from api.admin import router as admin_router
except Exception as exc:
    admin_router = None
    print("Admin router not loaded:", exc)

try:
    from api.mcp import router as mcp_router
except Exception as exc:
    mcp_router = None
    print("MCP router not loaded:", exc)

if admin_router:
    app.include_router(admin_router)

if mcp_router:
    app.include_router(mcp_router)


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    limit: int = Field(default=5, ge=1, le=20)
    max_chars_per_file: int = Field(default=6000, ge=1000, le=20000)


class SearchReadRequest(BaseModel):
    q: str = Field(..., min_length=1)
    limit: int = Field(default=5, ge=1, le=20)
    max_chars_per_file: int = Field(default=6000, ge=1000, le=20000)


def openai_client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise RuntimeError("Missing OPENAI_API_KEY environment variable.")
    return OpenAI(api_key=OPENAI_API_KEY)


def build_context(files: List[Dict[str, Any]], max_context_chars: int) -> str:
    blocks: List[str] = []
    used = 0

    for idx, file in enumerate(files, start=1):
        content = (file.get("content") or file.get("snippet") or "").strip()
        if not content:
            continue

        block = (
            f"[TÀI LIỆU {idx}]\n"
            f"Tên: {file.get('name')}\n"
            f"ID: {file.get('id')}\n"
            f"Link: {file.get('webViewLink')}\n"
            f"Nội dung:\n{content}\n"
        )

        if used + len(block) > max_context_chars:
            remaining = max_context_chars - used
            if remaining > 1000:
                blocks.append(block[:remaining])
            break

        blocks.append(block)
        used += len(block)

    return "\n---\n".join(blocks)


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "TRUNG_HUYEN_AI_OS",
        "message": "API is running"
    }
    if os_path_exists(index_path):
        return FileResponse(index_path)
    return {
        "system": "TRUNG_HUYEN_AI_OS",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
    }


def os_path_exists(path: str) -> bool:
    try:
        import os
        return os.path.exists(path)
    except Exception:
        return False

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print("========== REQUEST ==========")
    print("Method:", request.method)
    print("Path:", request.url.path)
    print("Query:", request.url.query)
    print("Headers:", dict(request.headers))
    response = await call_next(request)
    print("Status:", response.status_code)
    print("=============================")
    return response

@app.get("/health")
def health():
    return {
        "server": "ok",
        "version": "1.0.0",
        "google_service_account_json": bool(GOOGLE_SERVICE_ACCOUNT_JSON),
        "drive_folder_id": bool(DRIVE_FOLDER_ID),
        "openai_api_key": bool(OPENAI_API_KEY),
        "openai_model": OPENAI_MODEL,
        "mcp_loaded": bool(mcp_router),
    }

@app.get("/actions.json", include_in_schema=False)
def actions_schema():
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "Trung Huyen Knowledge Action",
            "version": "1.0.0"
        },
        "servers": [
            {
                "url": "https://trung-huyen-ai-779121307308.asia-southeast1.run.app"
            }
        ],
        "paths": {
            "/drive/files": {
                "get": {
                    "operationId": "listDriveFiles",
                    "summary": "List Google Drive files",
                    "description": "Liệt kê tài liệu trong Google Drive của Trung Huyền AI.",
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "integer",
                                "default": 5
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Danh sách tài liệu",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "folder_limited": {"type": "boolean"},
                                            "files": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {"type": "string"},
                                                        "name": {"type": "string"},
                                                        "mimeType": {"type": "string"},
                                                        "webViewLink": {"type": "string"},
                                                        "modifiedTime": {"type": "string"}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

            "/drive/search": {
                "get": {
                    "operationId": "searchDriveFiles",
                    "summary": "Search Google Drive files",
                    "description": "Tìm tài liệu trong Google Drive theo từ khóa.",
                    "parameters": [
                       {
                            "name": "q",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"}
                       },
                       {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer", "default": 5}
                       }
                    ],
                    "responses": {
                        "200": {
                            "description": "Kết quả tìm kiếm tài liệu",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "query": {"type": "string"},
                                            "files": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {"type": "string"},
                                                        "name": {"type": "string"},
                                                        "mimeType": {"type": "string"},
                                                        "webViewLink": {"type": "string"},
                                                        "modifiedTime": {"type": "string"}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
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
        return JSONResponse(status_code=500, content={"status": "error", "message": str(exc)})


@app.get("/drive/search")
def drive_search(q: str = Query(..., min_length=1), limit: int = Query(default=20, ge=1, le=100)):
    try:
        return {
            "status": "ok",
            "query": q,
            "files": search_files(q=q, limit=limit),
        }
    except Exception as exc:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(exc)})


@app.get("/drive/read")
def drive_read(file_id: str):
    try:
        content = read_file_content(file_id=file_id)
        return {
            "status": "ok",
            "file_id": file_id,
            "content_length": len(content),
            "content": content,
        }
    except Exception as exc:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(exc)})

@app.get("/actions.json", include_in_schema=False)
def actions_schema():
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Trung Huyen Knowledge Action",
            "version": "1.0.0"
        },
        "servers": [
            {
                "url": "https://trung-huyen-ai-779121307308.asia-southeast1.run.app"
            }
        ],
        "paths": {
            "/drive/files": {
                "get": {
                    "operationId": "listDriveFiles",
                    "summary": "List Google Drive files",
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "integer",
                                "default": 5
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "List of files from Google Drive",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "folder_limited": {"type": "boolean"},
                                            "files": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {"type": "string"},
                                                        "name": {"type": "string"},
                                                        "mimeType": {"type": "string"},
                                                        "webViewLink": {"type": "string"},
                                                        "modifiedTime": {"type": "string"}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
@app.post("/drive/search-read")
def drive_search_read(req: SearchReadRequest):
    try:
        files = search_and_read(
            q=req.q,
            limit=req.limit,
            max_chars_per_file=req.max_chars_per_file,
        )
        return {
            "status": "ok",
            "query": req.q,
            "files": files,
        }
    except Exception as exc:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(exc)})


@app.post("/chat")
def chat(req: ChatRequest):
    try:
        files = search_and_read(
            q=req.question,
            limit=req.limit,
            max_chars_per_file=req.max_chars_per_file,
        )

        sources = [
            {
                "name": f.get("name"),
                "id": f.get("id"),
                "mimeType": f.get("mimeType"),
                "link": f.get("webViewLink"),
                "modifiedTime": f.get("modifiedTime"),
                "score": f.get("score"),
            }
            for f in files
        ]

        context = build_context(files, MAX_CONTEXT_CHARS)
        if not context:
            return {
                "status": "ok",
                "answer": "Chưa đủ dữ liệu để kết luận. Server đã tìm trong Google Drive nhưng chưa đọc được tài liệu phù hợp với câu hỏi.",
                "sources": sources,
            }

        system = """
Bạn là AI Kiến Trúc Sư Trưởng của Hệ Điều Hành Bộ Não Gốc Trung Huyền Academy.

Luật trả lời:
1. Chỉ dùng dữ liệu được cung cấp trong phần TÀI LIỆU.
2. Không bịa thông tin ngoài tài liệu.
3. Nếu dữ liệu chưa đủ, nói đúng câu: "Chưa đủ dữ liệu để kết luận."
4. Khi phù hợp, phân biệt hiện tượng, nguyên nhân, bản chất và quy luật.
5. Ưu tiên tính nhất quán, khả năng mở rộng và kiến trúc dài hạn.
6. Trả lời bằng tiếng Việt, rõ ràng, thực tế.
"""

        user = f"""
CÂU HỎI:
{req.question}

DỮ LIỆU TỪ GOOGLE DRIVE:
{context}
"""

        response = openai_client().responses.create(
            model=OPENAI_MODEL,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )

        return {
            "status": "ok",
            "answer": response.output_text,
            "sources": sources,
        }

    except Exception as exc:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(exc)})
