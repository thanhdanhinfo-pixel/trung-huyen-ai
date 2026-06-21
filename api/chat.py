from typing import Any, Dict, List

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from openai import OpenAI
from pydantic import BaseModel, Field

from config import OPENAI_API_KEY, OPENAI_MODEL
from drive import search_and_read

router = APIRouter()


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    limit: int = Field(default=5, ge=1, le=20)
    max_chars_per_file: int = Field(default=6000, ge=1000, le=20000)


def openai_client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise RuntimeError("Missing OPENAI_API_KEY environment variable.")
    return OpenAI(api_key=OPENAI_API_KEY)


@router.post("/chat")
from services.workspace_service import load_workspace
    
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

        system = f"""

AI_KERNEL

{workspace["kernel"]}

AI_STATE

{workspace["state"]}

====================

Bạn phải tuân thủ AI_KERNEL.

Bạn phải làm việc theo AI_STATE.

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
