from __future__ import annotations

from fastapi import FastAPI


def configure_core_routers(app: FastAPI, *routers) -> None:
    for router in routers:
        app.include_router(router)


def include_optional_router(app: FastAPI, router, name: str) -> None:
    if router:
        app.include_router(router)
    else:
        print(f"{name} router not loaded")


def include_runtime_routers(
    app: FastAPI,
    *,
    admin_router=None,
    mcp_router=None,
    system_runtime_router=None,
    digital_twin_router=None,
    graph_router=None,
    system_status_router=None,
    rag_runtime_router=None,
    command_runner_router=None,
    observability_tools_router=None,
) -> None:
    """Register optional runtime routers in one place.

    This keeps app.py smaller while preserving existing import behavior.
    Required routers are still included directly in app.py until the next refactor phase.
    """
    include_optional_router(app, admin_router, "Admin")
    include_optional_router(app, mcp_router, "MCP")
    include_optional_router(app, system_runtime_router, "System runtime")
    include_optional_router(app, digital_twin_router, "Digital twin")
    include_optional_router(app, graph_router, "Graph")
    include_optional_router(app, system_status_router, "System status")
    include_optional_router(app, rag_runtime_router, "RAG runtime")
    include_optional_router(app, command_runner_router, "Command runner")
    include_optional_router(app, observability_tools_router, "Observability tools")
