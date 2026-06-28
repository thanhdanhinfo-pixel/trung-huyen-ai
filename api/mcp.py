from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field
from openai import OpenAI
from system.security import (
    is_founder_grant_active,
    is_founder_unlock_active,
    system_write,
    create_grant,
    load_grant,
    revoke_grant,
)
import os
import requests

from services.github_service import github_list_files, github_read_file, github_update_file
from services.execution_engine import execution_engine, execution_plan_from_dict
from config import OPENAI_API_KEY, OPENAI_MODEL, MAX_CONTEXT_CHARS
from drive import (
    list_files,
    read_file_content,
    search_and_read,
    append_google_doc,
    create_google_doc,
    create_folder,

)
from fastapi import Header, HTTPException
from config import MCP_API_KEY, DRIVE_FOLDER_ID, drive_root_sources
from system.security import (
    validate_founder_approval,
    write_audit,
    require_audit,
)

WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
GOVERNED_WRITE_PATH_PREFIXES = (
    "/github/update",
    "/github/delete",
    "/github/move",
    "/github/batch",
    "/github/cleanup",
    "/github/patch",
    "/github/patch-batch",
    "/github/move-batch",
    "/github/mkdir",
    "/github/refactor-imports",
)


def is_founder_approved(args: Dict[str, Any]) -> bool:
    return validate_founder_approval(args)

def is_emergency_override(args: Dict[str, Any]) -> bool:
    emergency = args.get("emergency_override")

    if not isinstance(emergency, dict):
        return False

    from system.security import is_emergency_active

    return is_emergency_active(emergency)

def preflight_context() -> Dict[str, Any]:
    return {
        "status": "READY_TO_EXECUTE",
        "tools": {
            "github_read": True,
            "github_write": True,
            "mcp": True,
            "drive": True,
            "runtime": True,
        },
        "required_sources": [
            "/system/khoi-dong",
            "/system/tool-health",
            "/system/global-memory",
            "/system/last-actions",
            "/system/next-actions",
            "system/CAPABILITY_REGISTRY.yaml",
        ],
        "policy": "OBSERVE_FIRST_VERIFY_CAPABILITIES_CONTINUE_FROM_SYSTEM_STATE",
    }
router = APIRouter(prefix="/mcp", tags=["MCP Gateway"])

APPS_SCRIPT_CREATE_DOCUMENT_URL = os.getenv(
    "APPS_SCRIPT_CREATE_DOCUMENT_URL",
    "https://script.google.com/macros/s/AKfycbySbNlbkHiferUvBGd2pvChnTbIEgswDMcDcU1X6pngDD57FN1XIP3X6zInjgboEhYohA/exec",
)


class MCPCall(BaseModel):
    tool: str = Field(..., min_length=1)
    arguments: Dict[str, Any] = Field(default_factory=dict)

def verify_mcp_key(
    x_api_key: str = "",
    authorization: str = "",
):
    bearer_key = authorization.replace("Bearer ", "").strip()
    provided_key = x_api_key or bearer_key

    if MCP_API_KEY and provided_key != MCP_API_KEY:
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


def _default_create_folder_id(parent_id: str | None = None) -> str:
    if parent_id:
        return parent_id
    if DRIVE_FOLDER_ID:
        return DRIVE_FOLDER_ID
    roots = drive_root_sources()
    if roots:
        return roots[0]["id"]
    raise RuntimeError("Missing parent_id, DRIVE_FOLDER_ID or KNOWLEDGE_SOURCES drive root.")


def create_document_via_apps_script(
    title: str,
    content: str = "",
    parent_id: str | None = None,
) -> Dict[str, Any]:
    folder_id = _default_create_folder_id(parent_id)

    response = requests.post(
        APPS_SCRIPT_CREATE_DOCUMENT_URL,
        json={
            "folderId": folder_id,
            "title": title,
            "content": content or "",
        },
        timeout=60,
    )

    try:
        data = response.json()
    except Exception:
        data = {"raw_response": response.text}

    if not response.ok:
        return {
            "status": "error",
            "provider": "apps_script",
            "status_code": response.status_code,
            "folderId": folder_id,
            "response": data,
        }

    return {
        "status": "ok",
        "provider": "apps_script",
        "folderId": folder_id,
        **data,
    }


@router.get("/tools")
def tools():
    return {
        "status": "ok",
        "tools": [
            "list_documents",
            "search_documents",
            "read_document",
            "ask_knowledge",
            "github_list_files",
            "github_read_file",
            "system_self_test",
            "github_update_file",
            "listDirectory",
            "readFile",
            "searchCode",
            "execute_plan",
            "backend_call",
            "system_tree",
            "workspace_bootstrap",
            "create_document",
            "append_document",
            "create_folder",
        ]
    }
    
@router.post("/call")
def call_tool(req: MCPCall, x_api_key: str = Header(default="")):
    if MCP_API_KEY and x_api_key != MCP_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid MCP API key")

    preflight = preflight_context()

    if preflight.get("status") != "READY_TO_EXECUTE":
        return {
            "status": "error",
            "tool": "preflight",
            "message": "System preflight failed",
            "preflight": preflight,
        }

    tool = req.tool
    args = req.arguments

    if tool == "backend_call":
        method = args.get("method", "GET").upper()
        path = args.get("path", "")
        body = args.get("body", None)

        if not path.startswith("/"):
            return {
                "status": "error",
                "tool": tool,
                "message": "path must start with /",
            }

        if is_governed_write_path(method, path):
            return {
                "status": "error",
                "tool": tool,
                "message": "Direct governed write endpoints are forbidden through backend_call. Use governed MCP tools only.",
                "path": path,
                "method": method,
            }

        url = f"http://127.0.0.1:8080{path}"

        try:
            if method == "GET":
                response = requests.get(url, timeout=60)
            elif method == "POST":
                response = requests.post(url, json=body, timeout=60)
            else:
                return {
                    "status": "error",
                    "tool": tool,
                    "message": f"Unsupported method: {method}",
                }

            try:
                data = response.json()
            except Exception:
                data = response.text

            return {
                "status": "ok" if response.ok else "error",
                "tool": tool,
                "status_code": response.status_code,
                "result": data,
            }

        except Exception as exc:
            return {
                "status": "error",
                "tool": tool,
                "message": str(exc),
            }
    if tool == "list_documents":
        limit = int(args.get("limit", 50))
        return {
            "status": "ok",
            "tool": tool,
            "files": list_files(limit=limit),
        }
    if tool == "workspace_bootstrap":
        from drive import list_recursive, read_by_path

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
                    {
                        "name": f.get("name"),
                        "path": f.get("path"),
                        "mimeType": f.get("mimeType"),
                    }
                    for f in files
                ],
            },
        }
    if tool == "listDirectory":
        path = args.get("path", "")
        try:
            return {
                "status": "ok",
                "tool": tool,
                "files": github_list_files(path),
            }
        except Exception as exc:
            return {
                "status": "error",
                "tool": tool,
                "message": str(exc),
                "type": type(exc).__name__,
            }

    if tool == "readFile":
        path = args.get("path", "")
        if not path:
            return {
                "status": "error",
                "tool": tool,
                "message": "path is required",
            }
        try:
            return {
                "status": "ok",
                "tool": tool,
                "result": github_read_file(path),
            }
        except Exception as exc:
            return {
                "status": "error",
                "tool": tool,
                "message": str(exc),
                "type": type(exc).__name__,
            }

    if tool == "searchCode":
        query = args.get("query", "") or args.get("q", "")
        if not query:
            return {
                "status": "error",
                "tool": tool,
                "message": "query is required",
            }
        try:
            files = github_list_files("")
            matches = []
            for item in files:
                path = item.get("path", "")
                if not path.endswith(".py"):
                    continue
                try:
                    data = github_read_file(path)
                    content = data.get("content", "") if isinstance(data, dict) else ""
                    if query in content or query in path:
                        matches.append({
                            "path": path,
                            "name": item.get("name"),
                        })
                except Exception:
                    continue
            return {
                "status": "ok",
                "tool": tool,
                "query": query,
                "matches": matches,
                "count": len(matches),
            }
        except Exception as exc:
            return {
                "status": "error",
                "tool": tool,
                "message": str(exc),
                "type": type(exc).__name__,
            }

    if tool == "github_list_files":
        path = args.get("path", "")
        return {
            "status": "ok",
            "tool": tool,
            "result": github_list_files(path),
        }

    if tool == "github_read_file":
        path = args.get("path", "")
        if not path:
            return {
                "status": "error",
                "tool": tool,
                "message": "path is required",
            }

        return {
            "status": "ok",
            "tool": tool,
            "result": github_read_file(path),
        }
    if tool == "system_self_test":
        from services.system_service import self_test

        return {
            "status": "ok",
            "tool": tool,
            "result": self_test(),
        }
    if tool == "system_tree":
        from drive import list_recursive
        return {
            "status": "ok",
            "tool": tool,
            "files": [
                {
                    "name": f.get("name"),
                    "path": f.get("path"),
                    "mimeType": f.get("mimeType"),
                }
                for f in list_recursive()
            ],
        }
    if tool == "founder_grant_open":
        grant = args.get("founder_grant", {})

        grant_token = create_grant(grant)

        return {
            "status": "ok",
            "tool": tool,
            "message": "Founder grant activated",
            "grant_token": grant_token,
            "grant": grant,
        }

    if tool == "founder_grant_close":

        grant_token = args.get("grant_token", "")

        if not grant_token:
            return {
                "status": "error",
                "tool": tool,
                "message": "grant_token is required",
            }

        revoke_grant(
            grant_token,
            reason="manual close",
        )

        return {
            "status": "ok",
            "tool": tool,
            "message": "Founder grant revoked",
            "grant_token": grant_token,
        }
    
    if tool == "github_update_file":
        approved = is_founder_approved(args)
        if not approved:
            return {
                "status": "error",
                "tool": tool,
                "message": "User approval is required",
            }

        path = args.get("path", "")
        content = args.get("content", "")
        sha = args.get("sha", "")
        message = args.get("message", "")
        audit = write_audit(
            "github_update_file",
            {
                "approved_by": args.get("approved_by"),
                "approval_id": args.get("approval_id"),
                "tool": tool,
                "status": "pending",
            },
        )

        if not require_audit(audit):
            return {
                "status": "error",
                "message": "audit validation failed",
            }

        if not path or not content or not message:
            return {
                "status": "error",
                "tool": tool,
                "message": "path, content and message are required",
            }

        grant_token = args.get("grant_token", "")
        grant = load_grant(grant_token) if grant_token else args.get("founder_grant", {})

        result = system_write(
            action="update_file",
            target=path,
            payload={
                "content": content,
                "message": message,
                "sha": sha,
            },
            founder_grant=grant,
        )

        return {
            "status": "ok" if result.get("status") != "error" else "error",
            "tool": tool,
            "result": result,
        }
        
    if tool == "execute_plan":
        grant_token = args.get("grant_token", "")
        grant = load_grant(grant_token) if grant_token else args.get("founder_grant", {})

        approved = (
            is_founder_approved(args)
            or is_emergency_override(args)
            or is_founder_unlock_active(args.get("founder_unlock"), min_level=3)
            or is_founder_grant_active(
                grant,
                subject="TRUNG_HUYEN_AI_OS",
                min_level=3,
                scope="ALL_SYSTEM",
            )
        )            

        if not approved:
            return {
                "status": "error",
                "tool": tool,
                "message": "User approval is required",
            }

        audit = write_audit(
            "execute_plan",
            {
                "approved_by": (
                    args.get("approved_by")
                    or args.get("founder_unlock", {}).get("approved_by")
                    or grant.get("granted_by")
                ),    
                "approval_id": (
                    args.get("approval_id")
                    or args.get("founder_unlock", {}).get("session_id")
                    or grant.get("session_id")
                ), 
                "tool": tool,
                "status": "pending",
            },
        )

        if not require_audit(audit):
            return {
                "status": "error",
                "message": "audit validation failed",
            }

        plan_data = args.get("plan") or {}

        if not isinstance(plan_data, dict):
            return {
                "status": "error",
                "tool": tool,
                "message": "plan must be an object",
            }

        plan = execution_plan_from_dict(plan_data)
        result = execution_engine.execute(
            plan=plan,
            approved=True,
        )

        return {
            "status": result.get("status"),
            "tool": tool,
            "result": result,
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
    if tool == "create_folder":
        name = args.get("name", "")
        parent_id = args.get("parent_id", None)
        approved = is_founder_approved(args)

        if not approved:
            return {
                "status": "error",
                "tool": tool,
                "message": "Create denied. User approval is required.",
            }

        if not name:
            return {
                "status": "error",
                "tool": tool,
                "message": "name is required.",
            }

        result = create_folder(
            name=name,
            parent_id=parent_id,
        )
        return {
        "status": "ok",
        "tool": tool,
        "result": result,
        }
    
    if tool == "create_document":
        title = args.get("title") or args.get("name") or ""
        content = args.get("content", "")
        parent_id = args.get("parent_id", None)
        approved = bool(args.get("approved", False))

        if not approved:
            return {
                "status": "error",
                "tool": tool,
                "message": "Create denied. User approval is required.",
            }

        if not title:
            return {
                "status": "error",
                "tool": tool,
                "message": "title is required.",
            }

        try:
            result = create_document_via_apps_script(
                title=title,
                content=content,
                parent_id=parent_id,
            )

            return {
                "status": result.get("status", "ok"),
                "tool": tool,
                "result": result,
            }

        except Exception as exc:
            return {
                "status": "error",
                "tool": tool,
                "message": str(exc),
                "error_type": type(exc).__name__,
            }

    if tool == "append_document":
        file_id = args.get("file_id", "")
        content = args.get("content", "")
        approved = is_founder_approved(args)

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

        if not question:
            return {
                "status": "error",
                "tool": tool,
                "message": "question is required",
            }

        files = search_and_read(
            q=question,
            limit=limit,
            max_chars_per_file=max_chars,
        )

        context = build_context(files)
        print("=" * 60)
        print("ASK_KNOWLEDGE_FILES:", len(files))
        print("ASK_KNOWLEDGE_CONTEXT_LEN:", len(context))
        print("ASK_KNOWLEDGE_CONTEXT_PREVIEW:", context[:1000])
        print("=" * 60)

        if not context:
            return {
                "status": "ok",
                "tool": tool,
                "answer": "Chưa đủ dữ liệu để kết luận.",
                "sources": files,
                "mode": "drive_first_no_context",
            }

        if not OPENAI_API_KEY:
            return {
                "status": "error",
                "tool": tool,
                "message": "Missing OPENAI_API_KEY.",
            }

        client = OpenAI(api_key=OPENAI_API_KEY)
        print("=" * 60)
        print("MODEL:", OPENAI_MODEL)
        print("QUESTION:", question)
        print("CONTEXT LENGTH:", len(context))
        print(context)
        print("=" * 60)
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=[
                {
                    "role": "system",
                    "content": (
                        "Bạn là AI của Trung Huyền Academy. "
                        "Chỉ trả lời dựa trên dữ liệu Google Drive được cung cấp. "
                        "Không dùng AI BRAIN CONTEXT. "
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

    return {
        "status": "error",
        "message": f"Unknown tool: {tool}",
    }


@router.get("/ping")
def ping():
    return {
        "status": "ok",
        "mcp": "alive",
    }
                
@router.get("/preflight")
def preflight():
    return preflight_context()

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
        x_api_key=MCP_API_KEY,
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
        x_api_key=MCP_API_KEY,
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
            },
            {
                "name": "execute_plan",
                "description": "Thực thi một kế hoạch chỉnh sửa GitHub qua Execution Engine sau khi người dùng phê duyệt"
            },
            {
                "name": "create_document",
                "description": "Tạo Google Docs mới sau khi người dùng phê duyệt"
            },
            {
                "name": "append_document",
                "description": "Thêm nội dung vào cuối Google Docs sau khi người dùng phê duyệt"
            }
        ]
    }


class BackendCallRequest(BaseModel):
    method: str = "GET"
    path: str
    body: Dict[str, Any] = {}


@router.post("/backend-call")
def backend_call_direct(req: BackendCallRequest, x_api_key: str = Header(default="")):
    if MCP_API_KEY and x_api_key != MCP_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid MCP API key")

    import requests

    if not req.path.startswith("/"):
        return {"status": "error", "message": "path must start with /"}

    url = f"http://127.0.0.1:8080{req.path}"
    method = req.method.upper()

    if method == "GET":
        response = requests.get(url, timeout=60)
    elif method == "POST":
        response = requests.post(url, json=req.body, timeout=60)
    else:
        return {"status": "error", "message": f"Unsupported method: {method}"}

    try:
        data = response.json()
    except Exception:
        data = response.text

    return {
        "status": "ok" if response.ok else "error",
        "status_code": response.status_code,
        "result": data,
    }

@router.post("/create-folder")
def create_folder_direct(req: dict):

    req["approved"] = True

    return call_tool(
        MCPCall(
            tool="create_folder",
            arguments=req,
        ),
        x_api_key=MCP_API_KEY,
    )


@router.post("/create-document")
def create_document_direct(req: dict):

    req["approved"] = True

    return call_tool(
        MCPCall(
            tool="create_document",
            arguments=req,
        ),
        x_api_key=MCP_API_KEY,
    )


@router.post("/append-document")
def append_document_direct(req: dict):

    req["approved"] = True

    return call_tool(
        MCPCall(
            tool="append_document",
            arguments=req,
        ),
        x_api_key=MCP_API_KEY,
    )
    

@router.get("/read-file")
def read_file_action(path: str = ""):
    if not path:
        return {
            "status": "error",
            "tool": "readFile",
            "message": "path is required",
        }

    try:
        return call_tool(
            MCPCall(
                tool="readFile",
                arguments={"path": path},
            ),
            x_api_key=MCP_API_KEY,
        )
    except Exception as exc:
        return {
            "status": "error",
            "tool": "readFile",
            "path": path,
            "message": str(exc),
            "type": type(exc).__name__,
        }


@router.get("/list-directory")
def list_directory_action(path: str = ""):
    try:
        return call_tool(
            MCPCall(
                tool="listDirectory",
                arguments={"path": path or ""},
            ),
            x_api_key=MCP_API_KEY,
        )
    except Exception as exc:
        return {
            "status": "error",
            "tool": "listDirectory",
            "path": path,
            "message": str(exc),
            "type": type(exc).__name__,
        }


@router.get("/search-code")
def search_code_action(query: str = ""):
    if not query:
        return {
            "status": "error",
            "tool": "searchCode",
            "message": "query is required",
        }

    try:
        return call_tool(
            MCPCall(
                tool="searchCode",
                arguments={"query": query},
            ),
            x_api_key=MCP_API_KEY,
        )
    except Exception as exc:
        return {
            "status": "error",
            "tool": "searchCode",
            "query": query,
            "message": str(exc),
            "type": type(exc).__name__,
        }


@router.get("/drive-tree")
def drive_tree():
    from drive import list_recursive

    return list_recursive()

@router.get("/bootstrap-system")
def bootstrap_system_direct():
    from services.bootstrap_service import bootstrap_system
    return bootstrap_system()

@router.get("/read-drive-file")
def read_drive_file_direct(file_id: str):
    from drive import read_file_content

    content = read_file_content(file_id=file_id)

    return {
        "status": "ok",
        "file_id": file_id,
        "content_length": len(content),
        "content": content,
    }

@router.get("/read-drive-path")
def read_drive_path(path: str):
    from drive import read_by_path

    return {
        "status": "ok",
        "path": path,
        "content": read_by_path(path),
    }
