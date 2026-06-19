from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


class Knowledge(BaseModel):
    title: str
    type: str
    content: str
    tags: list[str] = []


DATABASE = []


@router.post("/add")
def add_knowledge(item: Knowledge):
    DATABASE.append(item.model_dump())

    return {
        "status": "ok",
        "count": len(DATABASE)
    }


@router.get("/all")
def all_knowledge():
    return DATABASE
