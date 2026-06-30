from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["actions"])

@router.get("/actions.json", include_in_schema=False)
def actions_schema_redirect():
    return JSONResponse(
        status_code=501,
        content={
            "status": "pending_migration",
            "message": "actions.json migration scaffold created; move schema from app.py in next step"
        }
    )
