from fastapi import APIRouter
from services.system_service import self_test

router = APIRouter(
    prefix="/system",
    tags=["System"],
)

@router.get("/self-test")
def test():
    return self_test()
