from typing import Any, Dict, List
from api.github import router as github_router
from api.developer import router as developer_router
from api.repo import router as repo_router
from fastapi import FastAPI, Query
from api.knowledge import router as knowledge_router
from api.execute import router as execute_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI


from pydantic import BaseModel, Field
from fastapi import Request
from api.workspace import router as workspace_router
from config import (
    DRIVE_FOLDER_ID,
    GOOGLE_SERVICE_ACCOUNT_JSON,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    MAX_CONTEXT_CHARS,
    QDRANT_URL,
    QDRANT_API_KEY,
)
from drive import search_files, read_file_content, search_and_read, list_files


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
    import traceback
    print("MCP router not loaded")
    traceback.print_exc()
    mcp_router = None

if admin_router:
    app.include_router(admin_router)
app.include_router(github_router)
app.include_router(developer_router)
app.include_router(repo_router)

if mcp_router:
    app.include_router(mcp_router)
app.include_router(workspace_router)
    
app.include_router(knowledge_router)
app.include_router(execute_router)

from api.system import router as system_router

app.include_router(system_router)
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

@app.get("/version")
def version():
    return {
        "system": "TRUNG_HUYEN_AI_OS",
        "version": "1.0.0",
        "ai_brain": "v1",
        "rag": True,
        "qdrant": True,
        "drive": True,
    }
# =====================================
# SYSTEM
# =====================================
@app.get("/")
def root():
    index_path = "static/index.html"
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
    safe_headers = dict(request.headers)
    for key in ["authorization", "cookie", "x-api-key"]:
        if key in safe_headers:
            safe_headers[key] = "***REDACTED***"

    print("========== REQUEST ==========")
    print("Method:", request.method)
    print("Path:", request.url.path)
    print("Query:", request.url.query)
    print("Headers:", safe_headers)

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
        "qdrant_url": bool(QDRANT_URL),
        "qdrant_api_key": bool(QDRANT_API_KEY),
    }

@app.post("/rag/index")
def rag_index(limit: int = 10):
    try:
        return index_drive(limit=limit)
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(exc),
                "type": type(exc).__name__
            }
        ) 
# =====================================
# RAG
# =====================================

@app.post("/rag/init")
def rag_init():
    try:
        from vectordb import ensure_collection
        ensure_collection()
        return {
            "status": "ok",
            "message": "Qdrant collection ready"
        }
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(exc)
            }
        )    

@app.get("/actions.json", include_in_schema=False)
def actions_schema():
    basic_object = {
        "type": "object",
        "properties": {
            "status": {"type": "string"},
            "message": {"type": "string"},
        },
    }

    file_item = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "mimeType": {"type": "string"},
            "webViewLink": {"type": "string"},
            "modifiedTime": {"type": "string"},
            "size": {"type": "string"},
        },
    }

    return {
        "openapi": "3.1.0",
        "info": {
            "title": "Trung Huyen Knowledge Action",
            "version": "1.0.0",
        },
        "servers": [{"url": SERVER_URL}],
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
                            "schema": {"type": "integer", "default": 5},
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
                                                "items": file_item,
                                            },
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/drive/search": {
                "get": {
                    "operationId": "searchDriveFiles",
                    "summary": "Search Google Drive files",
                    "parameters": [
                        {
                            "name": "q",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer", "default": 5},
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Kết quả tìm kiếm",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "query": {"type": "string"},
                                            "files": {
                                                "type": "array",
                                                "items": file_item,
                                            },
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/drive/read": {
                "get": {
                    "operationId": "readDriveFile",
                    "summary": "Read Google Drive file content",
                    "parameters": [
                        {
                            "name": "file_id",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Nội dung tài liệu",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "file_id": {"type": "string"},
                                            "content_length": {"type": "integer"},
                                            "content": {"type": "string"},
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/drive/search-read": {
                "post": {
                    "operationId": "searchAndReadDrive",
                    "summary": "Search and read Google Drive documents",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["q"],
                                    "properties": {
                                        "q": {"type": "string"},
                                        "limit": {"type": "integer", "default": 5},
                                        "max_chars_per_file": {
                                            "type": "integer",
                                            "default": 6000,
                                        },
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Tài liệu kèm nội dung",
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
                                                        "modifiedTime": {"type": "string"},
                                                        "content": {"type": "string"},
                                                    },
                                                },
                                            },
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/chat": {
                "post": {
                    "operationId": "chatWithKnowledge",
                    "summary": "Ask Trung Huyen AI",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["question"],
                                    "properties": {
                                        "question": {"type": "string"},
                                        "limit": {"type": "integer", "default": 5},
                                        "max_chars_per_file": {
                                            "type": "integer",
                                            "default": 6000,
                                        },
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "AI trả lời dựa trên AI Brain",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "answer": {"type": "string"},
                                            "sources": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "name": {"type": "string"},
                                                        "link": {"type": "string"},
                                                        "score": {"type": "number"},
                                                        "chunk_index": {"type": "integer"},
                                                    },
                                                },
                                            },
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
        },
    }
# =====================================
# GOOGLE DRIVE
# =====================================

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
def drive_search(q: str, limit: int = Query(default=20, ge=1, le=200)):
    try:
        files = search_files(q=q, limit=limit)
        return {
            "status": "ok",
            "query": q,
            "files": files,
        }
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(exc)}
        )

@app.get("/rag/search")
def rag_search(q: str, limit: int = 5):
    try:
        return {
            "status": "ok",
            "query": q,
            "results": search_knowledge(q, limit)
        }
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(exc),
                "type": type(exc).__name__
            }
        )

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


@app.get("/rag/count")
def rag_count():
    try:
        from vectordb import client, COLLECTION_NAME, ensure_collection

        ensure_collection()

        result = client.count(
            collection_name=COLLECTION_NAME,
            exact=True
        )

        return {
            "status": "ok",
            "count": result.count
        }

    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(exc),
                "type": type(exc).__name__
            }
        )
# =====================================
# CHAT
# =====================================

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        knowledge = search_and_read(
            q=req.question,
            limit=req.limit,
            max_chars_per_file=req.max_chars_per_file,
        )

        context = "\n\n---\n\n".join(
            item.get("content", "")
            for item in knowledge
            if item.get("content")
        )

        sources = [
            {
                "name": item.get("name"),
                "link": item.get("webViewLink"),
                "id": item.get("id"),
                "mimeType": item.get("mimeType"),
            }
            for item in knowledge
        ]

        if not context:
            return {
                "status": "ok",
                "answer": "Chưa tìm thấy thông tin trong Google Drive.",
                "sources": sources,
            }

        system = """
Bạn là AI của Trung Huyền Academy.

Luật trả lời:
1. Chỉ dùng dữ liệu trong phần GOOGLE DRIVE CONTEXT.
2. Không dùng AI BRAIN CONTEXT.
3. Không bịa thông tin ngoài dữ liệu.
4. Nếu dữ liệu chưa đủ, nói đúng: "Chưa đủ dữ liệu để kết luận."
5. Trả lời bằng tiếng Việt, rõ ràng, thực tế.
"""

        user = f"""
CÂU HỎI:
{req.question}

GOOGLE DRIVE CONTEXT:
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
            "mode": "google_drive_only",
            "answer": response.output_text,
            "sources": sources,
        }

    except Exception as exc:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(exc)})                             
                                                
