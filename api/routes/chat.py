from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from services.chat_service import answer_from_drive

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    limit: int = Field(default=5, ge=1, le=20)
    max_chars_per_file: int = Field(default=6000, ge=1000, le=20000)


@router.post("/chat")
def chat(req: ChatRequest):
    try:
        return answer_from_drive(
            question=req.question,
            limit=req.limit,
            max_chars_per_file=req.max_chars_per_file,
        )
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(exc)},
        )
