def register_core_routers(app):
    from api.system import router as system_router
    from api.debug import router as debug_router
    from api.runtime import router as runtime_router
    from api.deployment import router as deployment_router
    from api.system_runtime import router as system_runtime_router
    from api.digital_twin import router as digital_twin_router
    from api.graph import router as graph_router

    app.include_router(system_router)
    app.include_router(debug_router)
    app.include_router(runtime_router)
    app.include_router(deployment_router)
    app.include_router(system_runtime_router)
    app.include_router(digital_twin_router)
    app.include_router(graph_router)
