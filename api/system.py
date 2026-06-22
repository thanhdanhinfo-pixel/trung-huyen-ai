from fastapi import APIRouter
from services.system_service import self_test

router = APIRouter(
    prefix="/system",
    tags=["System"],
)

@router.get("/self-test")
def test():
    return self_test()
@router.get("/files")
def files():
    from drive import list_recursive
    return {
        "status": "ok",
        "files": list_recursive()
    }
