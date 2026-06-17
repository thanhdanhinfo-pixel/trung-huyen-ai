from fastapi import Request

async def log_request(request: Request, call_next):
    response = await call_next(request)
    return response
