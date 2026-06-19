from fastapi import APIRouter
from pydantic import BaseModel, Field

from knowledge.capture import capture

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


class SaveKnowledgeRequest(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    type: str = "Principle"
    tags: list[str] = []


@router.post("/save")
def save_knowledge(req: SaveKnowledgeRequest):
    result = capture(
        title=req.title,
        content=req.content,
        knowledge_type=req.type,
    )

    return {
        "status": "ok",
        "saved": False,
        "stage": "captured",
        "message": "Knowledge captured as markdown. Drive saving will be added next.",
        "filename": result["filename"],
        "markdown": result["markdown"],
    }
