from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from collections import defaultdict, deque
from time import perf_counter, time
from uuid import uuid4

# Soft, per-instance rate limiting. This is not a distributed security control.
# Use Cloud Armor or Redis-backed counters for strict production enforcement.
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMITS = {
    "/chat": 30,
    "/drive/search-read": 20,
    "/rag/": 10,
}
_rate_limit_buckets: dict[str, deque[float]] = defaultdict(deque)

PAYLOAD_LIMITS = {
    "/chat": 50 * 1024,
    "/drive/search-read": 100 * 1024,
    "/rag/index": 200 * 1024,
}


def configure_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def register_request_logging(app: FastAPI, register_error) -> None:
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid4())
        request.state.request_id = request_id

        safe_headers = dict(request.headers)
        safe_headers["x-request-id"] = request_id
        for key in ["authorization", "cookie", "x-api-key"]:
            if key in safe_headers:
                safe_headers[key] = "***REDACTED***"

        payload_limit = PAYLOAD_LIMITS.get(request.url.path)
        content_length = int(request.headers.get("content-length", "0") or 0)
        if payload_limit and content_length > payload_limit:
            return JSONResponse(
                status_code=413,
                content={
                    "status": "error",
                    "code": "PAYLOAD_TOO_LARGE",
                    "limit_bytes": payload_limit,
                    "request_id": request_id,
                },
            )

        start = perf_counter()
        print(f"[req:{request_id}] start method={request.method} path={request.url.path} query={request.url.query}")
        print(f"[req:{request_id}] headers={safe_headers}")

        try:
            response = await call_next(request)
        except Exception as exc:  # noqa: BLE001
            latency_ms = round((perf_counter() - start) * 1000, 2)
            print(f"[req:{request_id}] error type={type(exc).__name__} latency_ms={latency_ms}")
            register_error(exc)
            raise

        latency_ms = round((perf_counter() - start) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = str(latency_ms)
        print(f"[req:{request_id}] done status={response.status_code} latency_ms={latency_ms}")
        return response


def configure_middlewares(app: FastAPI, register_error) -> None:
    configure_cors(app)
    register_request_logging(app, register_error)
