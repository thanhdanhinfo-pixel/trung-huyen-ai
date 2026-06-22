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
@router.get("/tree")
def tree():
    from drive import list_recursive
    files = list_recursive()
    return {
        "status": "ok",
        "count": len(files),
        "files": [
            {
                "name": f.get("name"),
                "path": f.get("path"),
                "mimeType": f.get("mimeType"),
            }
            for f in files
        ],
    }
