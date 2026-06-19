from typing import List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from knowledge.capture import capture

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


class SaveKnowledgeRequest(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    type: str = "Principle"
    tags: List[str] = []


@router.post("/save")
def save_knowledge(req: SaveKnowledgeRequest):
    result = capture(
        title=req.title,
        content=req.content,
        knowledge_type=req.type,
    )

    return {
    "status": "ok",
    "saved": True,
    "stage": "uploaded",
    "message": "Knowledge saved successfully.",
    "filename": result["filename"],
    "file_id": result["file_id"],
    "webViewLink": result["webViewLink"],
}
