from __future__ import annotations

import asyncio

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.app_startup import run_startup_boot
from api.developer import router as developer_router
from api.deployment import router as deployment_router
from api.debug import router as debug_router
from api.execute import router as execute_router
from api.github import router as github_router
from api.knowledge import router as knowledge_router
from api.repo import router as repo_router
from api.router_registry import include_runtime_routers
from api.routes.actions import router as actions_routes_router
from api.routes.chat import router as chat_routes_router
from api.routes.drive import router as drive_routes_router
from api.routes.rag import router as rag_routes_router
from api.routes.rag_runtime import router as rag_runtime_routes_router
from api.routes.system_core import router as system_core_routes_router
from api.runtime import router as runtime_router, register_error
from api.system import router as system_router
from api.system_awareness import router as system_awareness_router
from api.system_startup import router as system_startup_router
from api.workspace import router as workspace_router

SERVER_URL = "https://trung-huyen-ai-779121307308.asia-southeast1.run.app"

app = FastAPI(
    title="TRUNG_HUYEN_AI_OS",
    version="1.0.0",
    description="Bộ não AI kết nối Google Drive và OpenAI cho Trung Huyền Academy.",
    servers=[{"url": SERVER_URL}],
)

try:
    from bootstrap.boot import boot
except Exception as exc:
    print("Boot module not loaded:", exc)

    def boot():
        return None

try:
    from services.production_scheduler import production_scheduler
except Exception as exc:
    print("Production scheduler not loaded:", exc)

    class _NoopScheduler:
        def start(self):
            return None

    production_scheduler = _NoopScheduler()


@app.on_event("startup")
async def system_startup_boot():
    await run_startup_boot(boot=boot, production_scheduler=production_scheduler)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/dashboard", StaticFiles(directory="static/dashboard", html=True), name="dashboard")


def os_path_exists(path: str) -> bool:
    try:
        import os

        return os.path.exists(path)
    except Exception:
        return False


@app.get("/")
def root():
    index_path = "static/index.html"
    if os_path_exists(index_path):
        return FileResponse(index_path)

    return {
        "system": "TRUNG_HUYEN_AI_OS",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.middleware("http")
async def log_requests(request: Request, call_next):
    safe_headers = dict(request.headers)
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
    except Exception as exc:
        register_error(exc)
        raise

    print("Status:", response.status_code)
    print("=============================")
    return response


try:
    from api.admin import router as admin_router
except Exception as exc:
    admin_router = None
    print("Admin router not loaded:", exc)

try:
    from api.mcp import router as mcp_router
except Exception as exc:
    import traceback

    print("MCP router not loaded")
    traceback.print_exc()
    mcp_router = None

include_runtime_routers(
    app,
    admin_router=admin_router,
    mcp_router=mcp_router,
)

app.include_router(github_router)
app.include_router(developer_router)
app.include_router(repo_router)
app.include_router(workspace_router)
app.include_router(knowledge_router)
app.include_router(execute_router)
app.include_router(system_awareness_router)
app.include_router(system_startup_router)
app.include_router(drive_routes_router)
app.include_router(rag_routes_router)
app.include_router(rag_runtime_routes_router)
app.include_router(chat_routes_router)
app.include_router(system_core_routes_router)
app.include_router(actions_routes_router)
app.include_router(system_router)
app.include_router(debug_router)
app.include_router(runtime_router)
app.include_router(deployment_router)

try:
    from api.system_runtime import router as system_runtime_router
except Exception as exc:
    import traceback

    print("System runtime router not loaded")
    traceback.print_exc()
    system_runtime_router = None

try:
    from api.digital_twin import router as digital_twin_router
except Exception as exc:
    print("Digital twin router not loaded:", exc)
    digital_twin_router = None

try:
    from api.graph import router as graph_router
except Exception as exc:
    print("Graph router not loaded:", exc)
    graph_router = None

try:
    from api.system_status import router as system_status_router
except Exception as exc:
    print("System status router not loaded:", exc)
    system_status_router = None

try:
    from api.rag_runtime import router as rag_runtime_router
except Exception as exc:
    print("RAG runtime router not loaded:", exc)
    rag_runtime_router = None

try:
    from api.command_runner import router as command_runner_router
except Exception as exc:
    print("Command runner router not loaded:", exc)
    command_runner_router = None

try:
    from api.observability_tools import router as observability_tools_router
except Exception as exc:
    print("Observability tools router not loaded:", exc)
    observability_tools_router = None

include_runtime_routers(
    app,
    system_runtime_router=system_runtime_router,
    digital_twin_router=digital_twin_router,
    graph_router=graph_router,
    system_status_router=system_status_router,
    rag_runtime_router=rag_runtime_router,
    command_runner_router=command_runner_router,
    observability_tools_router=observability_tools_router,
)
