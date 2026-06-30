from typing import Any, Dict, List
from api.github import router as github_router
from api.developer import router as developer_router
from api.repo import router as repo_router
from fastapi import FastAPI, Query
from api.knowledge import router as knowledge_router
from api.execute import router as execute_router
from api.system_awareness import router as system_awareness_router
from api.system_startup import router as system_startup_router
from api.routes.drive import router as drive_routes_router
from api.routes.rag import router as rag_routes_router
from api.routes.rag_runtime import router as rag_runtime_routes_router
from api.routes.chat import router as chat_routes_router
from api.routes.system_core import router as system_core_routes_router
from api.app_startup import run_startup_boot
from api.router_registry import include_runtime_routers

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
from drive import (
    list_files,
    search_files,
    search_and_read,
    read_file_content,
    read_folder,
    find_file_by_path,
    get_path_index,
)
try:
    from rag.indexer import index_drive
except Exception:
    index_drive = None

try:
    from rag.search import search_knowledge
except Exception:
    search_knowledge = None


SERVER_URL = "https://trung-huyen-ai-779121307308.asia-southeast1.run.app"

app = FastAPI(
    title="TRUNG_HUYEN_AI_OS",
    version="1.0.0",
    description="Bộ não AI kết nối Google Drive và OpenAI cho Trung Huyền Academy.",
    servers=[{"url": SERVER_URL}],
)

try:
    from bootstrap.boot import boot
except Exception as exc:
    print("Boot module not loaded:", exc)
    def boot():
        return None

try:
    from services.production_scheduler import production_scheduler
except Exception as exc:
    print("Production scheduler not loaded:", exc)
    class _NoopScheduler:
        def start(self):
            return None
    production_scheduler = _NoopScheduler()

@app.on_event('startup')
async def system_startup_boot():
    await run_startup_boot(boot=boot, production_scheduler=production_scheduler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
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

include_runtime_routers(
    app,
    admin_router=admin_router,
    mcp_router=mcp_router,
)
app.include_router(github_router)
app.include_router(developer_router)
app.include_router(repo_router)
app.include_router(workspace_router)
    
app.include_router(knowledge_router)
app.include_router(execute_router)
app.include_router(system_awareness_router)
app.include_router(system_startup_router)
app.include_router(drive_routes_router)
app.include_router(rag_routes_router)
app.include_router(rag_runtime_routes_router)
app.include_router(chat_routes_router)
app.include_router(system_core_routes_router)

from api.system import router as system_router
from api.debug import router as debug_router

from api.runtime import router as runtime_router, register_error
from api.deployment import router as deployment_router

try:
    from api.system_runtime import router as system_runtime_router
except Exception as exc:
    import traceback
    print("System runtime router not loaded")
    traceback.print_exc()
    system_runtime_router = None

try:
    from api.digital_twin import router as digital_twin_router
except Exception as exc:
    print("Digital twin router not loaded:", exc)
    digital_twin_router = None

try:
    from api.graph import router as graph_router
except Exception as exc:
    print("Graph router not loaded:", exc)
    graph_router = None

try:
    from api.system_status import router as system_status_router
except Exception as exc:
    print("System status router not loaded:", exc)
    system_status_router = None

try:
    from api.rag_runtime import router as rag_runtime_router
except Exception as exc:
    print("RAG runtime router not loaded:", exc)
    rag_runtime_router = None

try:
    from api.command_runner import router as command_runner_router
except Exception as exc:
    print("Command runner router not loaded:", exc)
    command_runner_router = None

try:
    from api.observability_tools import router as observability_tools_router
except Exception as exc:
    print("Observability tools router not loaded:", exc)
    observability_tools_router = None

app.include_router(system_router)
app.include_router(debug_router)
app.include_router(runtime_router)
app.include_router(deployment_router)
include_runtime_routers(
    app,
    system_runtime_router=system_runtime_router,
    digital_twin_router=digital_twin_router,
    graph_router=graph_router,
    system_status_router=system_status_router,
    rag_runtime_router=rag_runtime_router,
    command_runner_router=command_runner_router,
    observability_tools_router=observability_tools_router,
)
app.mount('/dashboard', StaticFiles(directory='static/dashboard', html=True), name='dashboard')

# ChatRequest migrated to api.routes.chat

class SearchReadRequest(BaseModel):
    q: str = Field(..., min_length=1)
    limit: int = Field(default=5, ge=1, le=20)
    max_chars_per_file: int = Field(default=6000, ge=1000, le=20000)


# openai_client migrated to services.chat_service

# build_context migrated to services.chat_service

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

    try:
        response = await call_next(request)
    except Exception as exc:
        register_error(exc)
        raise

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

# /rag/index migrated to api.routes.rag_runtime
@app.post("/ping-post")
def ping_post():
    return {"status": "ok"}

# /drive/rebuild-index migrated to api.routes.drive
# =====================================
# RAG
# =====================================

# /rag/init migrated to api.routes.rag_runtime

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

# /drive/files migrated to api.routes.drive
# /drive/search migrated to api.routes.drive

# /rag/search migrated to api.routes.rag

# /drive/read migrated to api.routes.drive

# /drive/search-read migrated to api.routes.drive
# /rag/count migrated to api.routes.rag_runtime
# /drive/read-path migrated to api.routes.drive
# /drive/list-path migrated to api.routes.drive
# =====================================
# CHAT
# =====================================

# /chat migrated to api.routes.chat
