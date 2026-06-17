from fastapi import APIRouter
from services.index_service import build_index

router=APIRouter(prefix="/admin",tags=["Admin"])

@router.get("/index")
def index(limit:int=100):
    return {"status":"ok","documents":build_index(limit)}
