from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL, MAX_CONTEXT_CHARS
from drive import list_files, read_file_content, search_and_read, append_google_doc
from fastapi import Header, HTTPException
from config import MCP_API_KEY

router = APIRouter(prefix="/mcp", tags=["MCP Gateway"])


class MCPCall(BaseModel):
    tool: str = Field(..., min_length=1)
    arguments: Dict[str, Any] = Field(default_factory=dict)

def verify_mcp_key(x_api_key: str = Header(default="")):
    if MCP_API_KEY and x_api_key != MCP_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid MCP API key")

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
            "ask_knowledge",
            "append_document"
        ]
    }


@router.post("/call")
def call_tool(req: MCPCall, x_api_key: str = Header(default="")):
    if MCP_API_KEY and x_api_key != MCP_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid MCP API key")
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
       try:
          q = args.get("q", "")
          limit = int(args.get("limit", 5))
          max_chars = int(args.get("max_chars_per_file", 6000))

          files = search_and_read(
            q=q,
            limit=limit,
            max_chars_per_file=max_chars,
          )

          return {
              "status": "ok",
              "tool": tool,
              "query": q,
              "files": files,
          }

       except Exception as e:
          return {
              "status": "error",
              "error": str(e),
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
    if tool == "append_document":
        file_id = args.get("file_id", "")
        content = args.get("content", "")
        approved = bool(args.get("approved", False))

        if not approved:
            return {
                "status": "error",
                "tool": tool,
                "message": "Append denied. User approval is required.",
            }

        if not file_id or not content:
            return {
                "status": "error",
                "tool": tool,
                "message": "file_id and content are required.",
            }

        result = append_google_doc(file_id=file_id, content=content)

        return {
            "status": "ok",
            "tool": tool,
            "result": result,
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
        ),
        x_api_key=MCP_API_KEY
    )
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
        ),
        x_api_key=MCP_API_KEY
    )
@router.get("/manifest")
def manifest():
    return {
        "name": "TRUNG_HUYEN_CORE_MCP",
        "version": "1.0.0",
        "description": "MCP Gateway cho Bộ Não Gốc Trung Huyền Academy",
        "tools": [
            {
                "name": "list_documents",
                "description": "Liệt kê tài liệu trong kho tri thức"
            },
            {
                "name": "search_documents",
                "description": "Tìm và đọc tài liệu liên quan từ Google Drive"
            },
            {
                "name": "read_document",
                "description": "Đọc nội dung một tài liệu theo file_id"
            },
            {
                "name": "ask_knowledge",
                "description": "Trả lời câu hỏi dựa trên kho tri thức"
            }
        ]
    }
