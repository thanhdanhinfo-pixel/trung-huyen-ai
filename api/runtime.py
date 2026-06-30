from fastapi import APIRouter 
import traceback

router = APIRouter(prefix="/runtime", tags=["Runtime"])

RUNTIME_ERRORS = []

def register_error(exc: Exception):
    RUNTIME_ERRORS.append({
        "type": type(exc).__name__,
        "message": str(exc),
        "traceback": traceback.format_exc(),
    })

    if len(RUNTIME_ERRORS) > 100:
        del RUNTIME_ERRORS[:-100]


@router.get("/errors")
def errors():
    return {
        "status": "ok",
        "count": len(RUNTIME_ERRORS),
        "errors": RUNTIME_ERRORS[-20:],
    }


@router.get("/logs")
def logs():
    return {
        "status": "ok",
        "message": "Use Cloud Run logs integration in production."
    }
