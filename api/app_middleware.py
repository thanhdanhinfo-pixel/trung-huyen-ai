from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from time import perf_counter
from uuid import uuid4


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

        print("========== REQUEST ==========")
        print("Method:", request.method)
        print("Path:", request.url.path)
        print("Query:", request.url.query)
        print("Headers:", safe_headers)

        try:
            response = await call_next(request)
        except Exception as exc:  # noqa: BLE001
            register_error(exc)
            raise

        print("Status:", response.status_code)
        print("=============================")
        return response


def configure_middlewares(app: FastAPI, register_error) -> None:
    configure_cors(app)
    register_request_logging(app, register_error)
