from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

try:
    from rag.search import search_knowledge
except Exception:
    search_knowledge = None

router = APIRouter(prefix="/rag", tags=["rag"])


@router.get("/search")
def rag_search(q: str, limit: int = 5):
    if search_knowledge is None:
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "message": "search_knowledge not available",
            },
        )

    try:
        return {
            "status": "ok",
            "query": q,
            "results": search_knowledge(q, limit),
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
