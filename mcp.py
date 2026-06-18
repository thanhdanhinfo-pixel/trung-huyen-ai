from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import APIKeyHeader
from openai import OpenAI
from pydantic import BaseModel, Field

from config import MCP_API_KEY, OPENAI_API_KEY, OPENAI_MODEL, MAX_CONTEXT_CHARS
from drive import list_files, read_file_content, search_and_read


router = APIRouter(prefix="/mcp", tags=["MCP Gateway"])

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


def verify_mcp_key(x_api_key: Optional[str] = Depends(api_key_header)) -> None:
    if MCP_API_KEY and x_api_key != MCP_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid MCP API key")


class ListDocumentsArgs(BaseModel):
    limit: int = Field(default=50, ge=1, le=200)


class SearchDocumentsArgs(BaseModel):
    q: str = Field(..., min_length=1)
    limit: int = Field(default=5, ge=1, le=20)
    max_chars_per_file: int = Field(default=6000, ge=1000, le=20000)


class ReadDocumentArgs(BaseModel):
    file_id: str = Field(..., min_length=1)


class AskKnowledgeArgs(BaseModel):
    question: str = Field(..., min_length=1)
    limit: int = Field(default=5, ge=1, le=20)
    max_chars_per_file: int = Field(default=6000, ge=1000, le=20000)


class MCPCall(BaseModel):
    tool: Literal["list_documents", "search_documents", "read_document", "ask_knowledge"]
    arguments: Dict[str, Any] = Field(default_factory=dict)


def build_context(files: List[Dict[str, Any]]) -> str:
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

        if used + len(block) > MAX_CONTEXT_CHARS:
            break

        blocks.append(block)
        used += len(block)

    return "\n---\n".join(blocks)


@router.get("/ping")
def ping():
    return {"status": "ok", "mcp": "alive"}


@router.get("/tools")
def tools():
    return {
        "status": "ok",
        "tools": [
            {
                "name": "list_documents",
                "description": "Liệt kê tài liệu trong Google Drive",
            },
            {
                "name": "search_documents",
                "description": "Tìm tài liệu liên quan và trả về nội dung/snippet",
            },
            {
                "name": "read_document",
                "description": "Đọc nội dung đầy đủ của một tài liệu theo file_id",
            },
            {
                "name": "ask_knowledge",
                "description": "Trả lời câu hỏi dựa trên kho tri thức Google Drive",
            },
        ],
    }


@router.get("/manifest")
def manifest():
    return {
        "name": "TRUNG_HUYEN_CORE_MCP",
        "version": "1.0.0",
        "description": "MCP Gateway cho Bộ Não Gốc Trung Huyền Academy",
        "tools": tools()["tools"],
    }


@router.post("/call", dependencies=[Depends(verify_mcp_key)])
def call_tool(req: MCPCall):
    tool = req.tool
    args = req.arguments or {}

    if tool == "list_documents":
        parsed = ListDocumentsArgs(**args)
        return {
            "status": "ok",
            "tool": tool,
            "files": list_files(limit=parsed.limit),
        }

    if tool == "search_documents":
        parsed = SearchDocumentsArgs(**args)
        files = search_and_read(
            q=parsed.q,
            limit=parsed.limit,
            max_chars_per_file=parsed.max_chars_per_file,
        )
        return {
            "status": "ok",
            "tool": tool,
            "query": parsed.q,
            "files": files,
        }

    if tool == "read_document":
        parsed = ReadDocumentArgs(**args)
        content = read_file_content(file_id=parsed.file_id)
        return {
            "status": "ok",
            "tool": tool,
            "file_id": parsed.file_id,
            "content_length": len(content),
            "content": content,
        }

    if tool == "ask_knowledge":
        parsed = AskKnowledgeArgs(**args)
        files = search_and_read(
            q=parsed.question,
            limit=parsed.limit,
            max_chars_per_file=parsed.max_chars_per_file,
        )

        context = build_context(files)
        if not context:
            return {
                "status": "ok",
                "tool": tool,
                "answer": "Chưa đủ dữ liệu để kết luận.",
                "sources": files,
            }

        if not OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail="Missing OPENAI_API_KEY.")

        client = OpenAI(api_key=OPENAI_API_KEY)

        response = client.responses.create(
            model=OPENAI_MODEL,
            input=[
                {
                    "role": "system",
                    "content": (
                        "Bạn là AI Kiến Trúc Sư Trưởng của Hệ Điều Hành Bộ Não Gốc Trung Huyền Academy. "
                        "Chỉ trả lời dựa trên dữ liệu được cung cấp. Nếu chưa đủ dữ liệu, nói: "
                        "Chưa đủ dữ liệu để kết luận."
                    ),
                },
                {
                    "role": "user",
                    "content": f"CÂU HỎI:\n{parsed.question}\n\nDỮ LIỆU:\n{context}",
                },
            ],
        )

        return {
            "status": "ok",
            "tool": tool,
            "answer": response.output_text,
            "sources": files,
        }

    raise HTTPException(status_code=400, detail=f"Unknown tool: {tool}")


@router.get("/test-search")
def test_search(q: str = "Hệ quan sát", limit: int = 3):
    files = search_and_read(q=q, limit=limit, max_chars_per_file=3000)
    return {
        "status": "ok",
        "query": q,
        "files": files,
    }


@router.get("/test-ask")
def test_ask(q: str = "Hệ quan sát là gì?"):
    return call_tool(
        MCPCall(
            tool="ask_knowledge",
            arguments={
                "question": q,
                "limit": 3,
                "max_chars_per_file": 6000,
            },
        )
    )
