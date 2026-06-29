from fastapi import FastAPI

from api.app_middleware import configure_middlewares
from api.router_registry import include_runtime_routers
from api.runtime import register_error


def create_app() -> FastAPI:
    app = FastAPI(
        title="TRUNG_HUYEN_AI_OS",
        version="1.0.0",
        description="Application factory bootstrap",
    )

    configure_middlewares(app, register_error)

    # Router wiring will be migrated incrementally to keep production stable.
    include_runtime_routers(app)

    return app
