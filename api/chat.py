from typing import Any, Dict, List

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from openai import OpenAI
from pydantic import BaseModel, Field

from config import OPENAI_API_KEY, OPENAI_MODEL
from rag.search import search_knowledge

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
def chat(req: ChatRequest):
    try:
        knowledge = search_knowledge(req.question, limit=5)

        context = "\n\n---\n\n".join(
            item.get("content", "")
            for item in knowledge
            if item.get("content")
        )

        sources = [
            {
                "name": item.get("metadata", {}).get("name"),
                "link": item.get("metadata", {}).get("link"),
                "score": item.get("score"),
                "chunk_index": item.get("metadata", {}).get("chunk_index"),
            }
            for item in knowledge
        ]

        if not context:
            return {
                "status": "ok",
                "answer": "Chưa đủ dữ liệu để kết luận.",
                "sources": sources,
            }

        system = """
Bạn là AI Kiến Trúc Sư Trưởng của Hệ Điều Hành Bộ Não Gốc Trung Huyền Academy.

Luật trả lời:
1. Chỉ dùng dữ liệu trong phần AI BRAIN CONTEXT.
2. Không bịa thông tin ngoài dữ liệu.
3. Nếu dữ liệu chưa đủ, nói đúng: "Chưa đủ dữ liệu để kết luận."
4. Khi phù hợp, phân biệt hiện tượng, nguyên nhân, bản chất và quy luật.
5. Trả lời bằng tiếng Việt, rõ ràng, thực tế.
"""

        user = f"""
CÂU HỎI:
{req.question}

AI BRAIN CONTEXT:
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
