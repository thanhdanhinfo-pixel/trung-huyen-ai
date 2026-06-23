from fastapi import APIRouter
from fastapi.responses import JSONResponse
from openai import OpenAI
from pydantic import BaseModel, Field

from config import OPENAI_API_KEY, OPENAI_MODEL
from drive import search_and_read

router = APIRouter(tags=["Chat"])


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    limit: int = Field(default=5, ge=1, le=20)
    max_chars_per_file: int = Field(default=6000, ge=1000, le=20000)


def openai_client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise RuntimeError("Missing OPENAI_API_KEY environment variable.")
    return OpenAI(api_key=OPENAI_API_KEY)


def load_workspace_context() -> dict:
    try:
        from services.workspace_service import load_workspace

        workspace = load_workspace()
        if isinstance(workspace, dict):
            return workspace
    except Exception:
        pass

    return {"kernel": "", "state": ""}


@router.post("/chat")
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
                "answer": "Chưa đủ dữ liệu để kết luận.",
                "sources": sources,
            }

        workspace = load_workspace_context()
        system = f"""
Bạn là AI của Trung Huyền Academy.

Luật trả lời:
1. Ưu tiên dùng dữ liệu trong phần GOOGLE DRIVE CONTEXT.
2. Không bịa thông tin ngoài dữ liệu.
3. Nếu dữ liệu chưa đủ, nói đúng: "Chưa đủ dữ liệu để kết luận."
4. Trả lời bằng tiếng Việt, rõ ràng, thực tế.

AI_KERNEL:
{workspace.get("kernel", "")}

AI_STATE:
{workspace.get("state", "")}
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
            "mode": "google_drive_with_workspace",
            "answer": response.output_text,
            "sources": sources,
        }

    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(exc),
                "type": type(exc).__name__,
            },
        )
