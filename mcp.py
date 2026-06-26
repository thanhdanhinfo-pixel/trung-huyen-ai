from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Header, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field

from config import MCP_API_KEY, OPENAI_API_KEY, OPENAI_MODEL, MAX_CONTEXT_CHARS
from drive import (
    GOOGLE_FOLDER,
    list_files,
    list_recursive,
    list_files_recursive,
    read_file_content,
    search_and_read,
    create_folder,
    create_google_doc,
    append_google_doc,
)
from services.github_service import (
    github_list_files,
    github_read_file,
    github_update_file,
)
from services.execution_engine import execution_engine, execution_plan_from_dict


router = APIRouter(prefix="/mcp", tags=["MCP Gateway"])


class MCPCall(BaseModel):
    tool: str = Field(..., min_length=1)
    arguments: Dict[str, Any] = Field(default_factory=dict)


class BackendCallRequest(BaseModel):
    method: str = "GET"
    path: str
    body: Dict[str, Any] = Field(default_factory=dict)


def verify_mcp_key(x_api_key: str = "") -> None:
    if MCP_API_KEY and x_api_key != MCP_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid MCP API key")


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


def tool_names() -> List[str]:
    return [
        "list_documents",
        "search_documents",
        "read_document",
        "ask_knowledge",
        "github_list_files",
        "github_read_file",
        "github_update_file",
        "execute_plan",
        "backend_call",
        "system_tree",
        "workspace_bootstrap",
        "create_folder",
        "create_document",
        "append_document",
    ]


@router.get("/ping")
def ping():
    return {"status": "ok", "mcp": "alive"}


@router.get("/tools")
def tools():
    return {"status": "ok", "tools": tool_names()}


@router.get("/manifest")
def manifest():
    return {
        "name": "TRUNG_HUYEN_CORE_MCP",
        "version": "2.0.0",
        "description": "MCP Gateway cho Bộ Não Gốc Trung Huyền Academy",
        "tools": [
            {"name": "list_documents", "description": "Liệt kê tài liệu trong kho tri thức"},
            {"name": "search_documents", "description": "Tìm và đọc tài liệu liên quan từ Google Drive"},
            {"name": "read_document", "description": "Đọc nội dung một tài liệu theo file_id"},
            {"name": "ask_knowledge", "description": "Trả lời câu hỏi dựa trên kho tri thức"},
            {"name": "github_list_files", "description": "Liệt kê file trong GitHub repository"},
            {"name": "github_read_file", "description": "Đọc file trong GitHub repository"},
            {"name": "github_update_file", "description": "Cập nhật file GitHub sau khi được phê duyệt"},
            {"name": "execute_plan", "description": "Thực thi kế hoạch chỉnh sửa sau khi được phê duyệt"},
            {"name": "backend_call", "description": "Gọi endpoint nội bộ của backend"},
            {"name": "system_tree", "description": "Lấy cây thư mục Google Drive"},
            {"name": "workspace_bootstrap", "description": "Nạp trạng thái workspace ban đầu"},
            {"name": "drive_list_children", "description": "Liệt kê trực tiếp con của một Google Drive folder theo folder_id"},
            {"name": "drive_tree", "description": "Lấy cây Google Drive có giới hạn depth để tránh response quá lớn"},
            {"name": "drive_index", "description": "Lập chỉ mục Google Drive có giới hạn theo folder_id và limit"},
            {"name": "create_folder", "description": "Tạo thư mục Google Drive sau khi được phê duyệt"},
            {"name": "create_document", "description": "Tạo Google Docs mới sau khi được phê duyệt"},
            {"name": "append_document", "description": "Thêm nội dung vào cuối Google Docs sau khi được phê duyệt"},
        ],
    }


@router.post("/call")
def call_tool(req: MCPCall, x_api_key: str = Header(default="")):
    verify_mcp_key(x_api_key)

    tool = req.tool
    args = req.arguments or {}

    if tool == "list_documents":
        limit = int(args.get("limit", 50))
        return {"status": "ok", "tool": tool, "files": list_files(limit=limit)}

    if tool == "search_documents":
        q = args.get("q", "")
        limit = int(args.get("limit", 5))
        max_chars = int(args.get("max_chars_per_file", 6000))
        files = search_and_read(q=q, limit=limit, max_chars_per_file=max_chars)
        return {"status": "ok", "tool": tool, "query": q, "files": files}

    if tool == "read_document":
        file_id = args.get("file_id", "")
        if not file_id:
            return {"status": "error", "tool": tool, "message": "file_id is required"}
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

        if not question:
            return {"status": "error", "tool": tool, "message": "question is required"}

        files = search_and_read(q=question, limit=limit, max_chars_per_file=max_chars)
        context = build_context(files)

        if not context:
            return {
                "status": "ok",
                "tool": tool,
                "answer": "Chưa đủ dữ liệu để kết luận.",
                "sources": files,
                "mode": "drive_first_no_context",
            }

        if not OPENAI_API_KEY:
            return {"status": "error", "tool": tool, "message": "Missing OPENAI_API_KEY."}

        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=[
                {
                    "role": "system",
                    "content": (
                        "Bạn là AI của Trung Huyền Academy. "
                        "Chỉ trả lời dựa trên dữ liệu Google Drive được cung cấp. "
                        "Nếu dữ liệu chưa đủ, nói: Chưa đủ dữ liệu để kết luận."
                    ),
                },
                {
                    "role": "user",
                    "content": f"CÂU HỎI:\n{question}\n\nDỮ LIỆU GOOGLE DRIVE:\n{context}",
                },
            ],
        )
        return {
            "status": "ok",
            "tool": tool,
            "answer": response.output_text,
            "sources": files,
            "mode": "google_drive_only",
        }

    if tool == "github_list_files":
        path = args.get("path", "")
        return {"status": "ok", "tool": tool, "result": github_list_files(path)}

    if tool == "github_read_file":
        path = args.get("path", "")
        if not path:
            return {"status": "error", "tool": tool, "message": "path is required"}
        return {"status": "ok", "tool": tool, "result": github_read_file(path)}

    if tool == "github_update_file":
        approved = bool(args.get("approved", False))
        if not approved:
            return {"status": "error", "tool": tool, "message": "User approval is required"}
        path = args.get("path", "")
        content = args.get("content", "")
        sha = args.get("sha", "")
        message = args.get("message", "")
        if not path or not content or not sha or not message:
            return {"status": "error", "tool": tool, "message": "path, content, sha and message are required"}
        return {"status": "ok", "tool": tool, "result": github_update_file(path, content, sha, message)}

    if tool == "execute_plan":
        approved = bool(args.get("approved", False))
        plan_data = args.get("plan") or {}
        if not isinstance(plan_data, dict):
            return {"status": "error", "tool": tool, "message": "plan must be an object"}
        plan = execution_plan_from_dict(plan_data)
        result = execution_engine.execute(plan=plan, approved=approved)
        return {"status": result.get("status"), "tool": tool, "result": result}

    if tool == "backend_call":
        method = args.get("method", "GET").upper()
        path = args.get("path", "")
        body = args.get("body", None)
        return _backend_call(method=method, path=path, body=body)

    if tool == "system_tree":
        from drive import list_recursive
        return {
            "status": "ok",
            "tool": tool,
            "files": [
                {"name": f.get("name"), "path": f.get("path"), "mimeType": f.get("mimeType")}
                for f in list_recursive()
            ],
        }

    if tool == "workspace_bootstrap":
        from drive import read_by_path
        files = list_recursive()
        protocol_path = "09_INFRASTRUCTURE/AI_PROTOCOLS/00_AI_PROTOCOL"
        state_path = "07_AI_FACTORY/00_AI_STATE.md"
        kernel_path = "07_AI_FACTORY/00_AI_KERNEL"
        return {
            "status": "ok",
            "tool": tool,
            "workspace": {
                "protocol_path": protocol_path,
                "state_path": state_path,
                "kernel_path": kernel_path,
                "protocol": read_by_path(protocol_path),
                "state": read_by_path(state_path),
                "kernel": read_by_path(kernel_path),
                "tree": [
                    {"name": f.get("name"), "path": f.get("path"), "mimeType": f.get("mimeType")}
                    for f in files
                ],
            },
        }

    if tool == "drive_list_children":
        folder_id = args.get("folder_id") or None
        limit = min(int(args.get("limit", 100)), 500)
        files = list_files(limit=limit, folder_id=folder_id)
        folders = [f for f in files if f.get("mimeType") == GOOGLE_FOLDER]
        documents = [f for f in files if f.get("mimeType") != GOOGLE_FOLDER]
        return {
            "status": "ok",
            "tool": tool,
            "folder_id": folder_id,
            "limit": limit,
            "count": len(files),
            "folder_count": len(folders),
            "document_count": len(documents),
            "folders": folders,
            "documents": documents,
        }

    if tool == "drive_tree":
        folder_id = args.get("folder_id") or None
        depth = max(1, min(int(args.get("depth", 2)), 6))
        limit = min(int(args.get("limit", 300)), 1000)
        items = list_recursive(parent_id=folder_id)
        scoped = []
        for item in items:
            path = item.get("path", item.get("name", ""))
            if not path:
                continue
            item_depth = len([part for part in path.split("/") if part])
            if item_depth <= depth:
                scoped.append({
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "path": path,
                    "mimeType": item.get("mimeType"),
                    "modifiedTime": item.get("modifiedTime"),
                    "webViewLink": item.get("webViewLink"),
                    "source": item.get("source"),
                    "source_id": item.get("source_id"),
                })
            if len(scoped) >= limit:
                break
        return {
            "status": "ok",
            "tool": tool,
            "folder_id": folder_id,
            "depth": depth,
            "limit": limit,
            "count": len(scoped),
            "items": scoped,
        }

    if tool == "drive_index":
        folder_id = args.get("folder_id") or None
        limit = min(int(args.get("limit", 500)), 2000)
        files = list_files_recursive(folder_id=folder_id, limit=limit)
        folders = [f for f in files if f.get("mimeType") == GOOGLE_FOLDER]
        documents = [f for f in files if f.get("mimeType") != GOOGLE_FOLDER]
        by_mime = {}
        for item in files:
            mime = item.get("mimeType", "unknown")
            by_mime[mime] = by_mime.get(mime, 0) + 1
        return {
            "status": "ok",
            "tool": tool,
            "folder_id": folder_id,
            "limit": limit,
            "total_count": len(files),
            "folder_count": len(folders),
            "document_count": len(documents),
            "by_mime": by_mime,
            "folders": folders,
            "documents": documents,
        }

    if tool == "create_folder":
        approved = bool(args.get("approved", False))
        if not approved:
            return {"status": "error", "tool": tool, "message": "Create denied. User approval is required."}
        name = args.get("name", "")
        parent_id = args.get("parent_id")
        if not name:
            return {"status": "error", "tool": tool, "message": "name is required"}
        folder = create_folder(name=name, parent_id=parent_id)
        return {"status": "ok", "tool": tool, "folder": folder}

    if tool == "create_document":
        approved = bool(args.get("approved", False))
        if not approved:
            return {"status": "error", "tool": tool, "message": "Create denied. User approval is required."}
        title = args.get("title") or args.get("name") or ""
        content = args.get("content", "")
        parent_id = args.get("parent_id")
        if not title:
            return {"status": "error", "tool": tool, "message": "title is required"}
        doc = create_google_doc(name=title, content=content, parent_id=parent_id)
        return {"status": "ok", "tool": tool, "document": doc}

    if tool == "append_document":
        approved = bool(args.get("approved", False))
        if not approved:
            return {"status": "error", "tool": tool, "message": "Append denied. User approval is required."}
        file_id = args.get("file_id", "")
        content = args.get("content", "")
        if not file_id or not content:
            return {"status": "error", "tool": tool, "message": "file_id and content are required"}
        result = append_google_doc(file_id=file_id, content=content)
        return {"status": "ok", "tool": tool, "result": result}

    return {"status": "error", "message": f"Unknown tool: {tool}"}


def _backend_call(method: str, path: str, body: Optional[Dict[str, Any]] = None):
    import requests

    if not path.startswith("/"):
        return {"status": "error", "message": "path must start with /"}

    url = f"http://127.0.0.1:8080{path}"
    method = method.upper()

    try:
        if method == "GET":
            response = requests.get(url, timeout=60)
        elif method == "POST":
            response = requests.post(url, json=body, timeout=60)
        else:
            return {"status": "error", "message": f"Unsupported method: {method}"}

        try:
            data = response.json()
        except Exception:
            data = response.text

        return {"status": "ok" if response.ok else "error", "status_code": response.status_code, "result": data}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@router.post("/backend-call")
def backend_call_direct(req: BackendCallRequest, x_api_key: str = Header(default="")):
    verify_mcp_key(x_api_key)
    return _backend_call(method=req.method, path=req.path, body=req.body)


@router.get("/test-search")
def test_search(q: str = "Hệ quan sát", limit: int = 3):
    return call_tool(
        MCPCall(
            tool="search_documents",
            arguments={"q": q, "limit": limit, "max_chars_per_file": 3000},
        ),
        x_api_key=MCP_API_KEY,
    )


@router.get("/test-ask")
def test_ask(q: str = "Hệ quan sát là gì?"):
    return call_tool(
        MCPCall(
            tool="ask_knowledge",
            arguments={"question": q, "limit": 3, "max_chars_per_file": 6000},
        ),
        x_api_key=MCP_API_KEY,
    )
