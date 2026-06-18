from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL, MAX_CONTEXT_CHARS
from drive import list_files, read_file_content, search_and_read

router = APIRouter(prefix="/mcp", tags=["MCP Gateway"])


class MCPCall(BaseModel):
    tool: str = Field(..., min_length=1)
    arguments: Dict[str, Any] = Field(default_factory=dict)


def build_context(files: List[Dict[str, Any]]) -> str:
    blocks = []
    used = 0

    for idx, file in enumerate(files, start=1):
        content = (file.get("content") or "").strip()
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


@router.get("/tools")
def tools():
    return {
        "status": "ok",
        "tools": [
            "list_documents",
            "search_documents",
            "read_document",
            "ask_knowledge"
        ]
    }


@router.post("/call")
def call_tool(req: MCPCall):
    tool = req.tool
    args = req.arguments

    if tool == "list_documents":
        limit = int(args.get("limit", 50))
        return {
            "status": "ok",
            "tool": tool,
            "files": list_files(limit=limit),
        }

    if tool == "search_documents":
        q = args.get("q", "")
        limit = int(args.get("limit", 5))
        max_chars = int(args.get("max_chars_per_file", 6000))
        return {
            "status": "ok",
            "tool": tool,
            "query": q,
            "files": search_and_read(q=q, limit=limit, max_chars_per_file=max_chars),
        }

    if tool == "read_document":
        file_id = args.get("file_id", "")
        content = read_file_content(file_id=file_id)
        return {
            "status": "ok",
            "tool": tool,
            "file_id": file_id,
            "content_length": len(content),
            "content": content,
        }

    if tool == "ask_knowledge":
        question = args.get("question", "")
        limit = int(args.get("limit", 5))
        max_chars = int(args.get("max_chars_per_file", 6000))

        files = search_and_read(
            q=question,
            limit=limit,
            max_chars_per_file=max_chars,
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
            return {
                "status": "error",
                "tool": tool,
                "message": "Missing OPENAI_API_KEY.",
            }

        client = OpenAI(api_key=OPENAI_API_KEY)

        response = client.responses.create(
            model=OPENAI_MODEL,
            input=[
                {
                    "role": "system",
                    "content": "Chỉ trả lời dựa trên dữ liệu được cung cấp. Nếu chưa đủ dữ liệu, nói: Chưa đủ dữ liệu để kết luận.",
                },
                {
                    "role": "user",
                    "content": f"CÂU HỎI:\n{question}\n\nDỮ LIỆU:\n{context}",
                },
            ],
        )

        return {
            "status": "ok",
            "tool": tool,
            "answer": response.output_text,
            "sources": files,
        }

    return {
        "status": "error",
        "message": f"Unknown tool: {tool}",
  }
@router.get("/ping")
def ping():
    return {
        "status": "ok",
        "mcp": "alive"
    }
@router.get("/test-search")
def test_search(q: str = "Hệ quan sát", limit: int = 3):
    return call_tool(
        MCPCall(
            tool="search_documents",
            arguments={
                "q": q,
                "limit": limit,
                "max_chars_per_file": 3000,
            },
        )
    )
