from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Any, Dict, List

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI

from config import (
    DRIVE_FOLDER_ID,
    GOOGLE_SERVICE_ACCOUNT_JSON,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    MAX_CONTEXT_CHARS,
)
from drive import list_files, search_files, read_file_content, search_and_read

try:
    from api.admin import router as admin_router
except Exception:
    admin_router = None
    
app = FastAPI(
    title="TRUNG_HUYEN_AI_OS",
    version="1.0.0",
    description="Bộ não AI kết nối Google Drive và OpenAI cho Trung Huyền Academy.",
)
mcp_router = None

try:
    from api.mcp import router as mcp_router
    app.include_router(mcp_router)
    print("MCP loaded")
except Exception ONResponse exc:
    print("MCP router not loaded:", exc)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

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


@app.get("/")
def root():
    return FileResponse("static/index.html")

from fastapi.responses import JSONResponse

@app.get("/openapi-mcp.json", include_in_schema=False)
def openapi_mcp():
    return JSONResponse({
        "openapi": "3.1.0",
        "info": {
            "title": "TRUNG_HUYEN_CORE_MCP",
            "description": "MCP API cho ChatGPT",
            "version": "1.0.0"
        },
        "servers": [
            {
                "url": "https://trung-huyen-ai-779121307308.asia-southeast1.run.app"
            }
        ],
        "security": [
            {
                "ApiKeyAuth": []
            }
        ],
        "components": {
            "securitySchemes": {
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "x-api-key"
                }
            },
            "schemas": {
                "McpRequest": {
                    "type": "object",
                    "required": [
                        "tool",
                        "arguments"
                    ],
                    "properties": {
                        "tool": {
                            "type": "string",
                            "enum": [
                                "ask_knowledge",
                                "search_documents",
                                "read_document",
                                "list_documents"
                            ]
                        },
                        "arguments": {
                            "type": "object"
                        }
                    }
                }
            }
        },
        "paths": {
            "/mcp/call": {
                "post": {
                    "operationId": "callMcpTool",
                    "summary": "Call MCP Tool",
                    "description": "Thực thi một công cụ MCP",
                    "security": [
                        {
                            "ApiKeyAuth": []
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/McpRequest"
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Success"
                        },
                        "400": {
                            "description": "Bad Request"
                        },
                        "401": {
                            "description": "Unauthorized"
                        },
                        "500": {
                            "description": "Server Error"
                        }
                    }
                }
            }
        }
    })
@app.get("/health")
def health():
    return {
        "server": "ok",
        "version": "1.0.0",
        "google_service_account_json": bool(GOOGLE_SERVICE_ACCOUNT_JSON),
        "drive_folder_id": bool(DRIVE_FOLDER_ID),
        "openai_api_key": bool(OPENAI_API_KEY),
        "openai_model": OPENAI_MODEL,
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


def build_context(files: List[Dict[str, Any]], max_context_chars: int) -> str:
    blocks: List[str] = []
    used = 0

    for idx, file in enumerate(files, start=1):
        content = file.get("content", "").strip()
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


if admin_router:
    app.include_router(admin_router)
