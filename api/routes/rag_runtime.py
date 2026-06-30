from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

try:
    from rag.indexer import index_drive
except Exception:
    index_drive = None

router = APIRouter(prefix="/rag", tags=["rag-runtime"])


@router.post("/index")
def rag_index(limit: int = 10):
    if index_drive is None:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "message": "index_drive not available"},
        )

    try:
        return index_drive(limit=limit)
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(exc), "type": type(exc).__name__},
        )


@router.post("/init")
def rag_init():
    try:
        from vectordb import ensure_collection

        ensure_collection()
        return {"status": "ok", "message": "Qdrant collection ready"}
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(exc)},
        )


@router.get("/count")
def rag_count():
    try:
        from vectordb import client, COLLECTION_NAME, ensure_collection

        ensure_collection()
        result = client.count(collection_name=COLLECTION_NAME, exact=True)
        return {"status": "ok", "count": result.count}
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(exc), "type": type(exc).__name__},
        )
