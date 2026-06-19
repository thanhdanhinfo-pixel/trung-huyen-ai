from fastapi import APIRouter
from pydantic import BaseModel

from knowledge.capture import capture

router = APIRouter(tags=["Knowledge"])


class SaveKnowledgeRequest(BaseModel):
    title: str
    content: str


@router.post("/knowledge/save")
def save_knowledge(req: SaveKnowledgeRequest):

    result = capture(
        title=req.title,
        content=req.content,
    )

    return {
        "status": "ok",
        "saved": False,
        "message": "Knowledge captured successfully.",
        "filename": result["filename"],
        "markdown": result["markdown"],
    }
