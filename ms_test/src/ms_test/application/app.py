"""FastAPI application factory for ms_test."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from ms_test.application.config.container import Container
from ms_test.application.config.config import Settings
from ms_test.infrastructure.entry_points.api.v1 import rest_controller
from ms_test.infrastructure.entry_points.api.v1.exception_handler import (
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Wire the DI container on startup and unwire on shutdown."""
    container: Container = app.state.container  # type: ignore[attr-defined]
    container.wire(
        modules=[
            rest_controller,
        ]
    )
    logger.info("Application startup complete.")
    # Uncomment to initialize async resources on startup, if needed
    # await container.resource_container.init_resources()
    yield
    container.unwire()
    # Uncomment the following line if you have async resources to shutdown
    # await container.resource_container.shutdown_resources()
    logger.info("Application shutdown complete.")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = Settings()
    container = Container()

    app = FastAPI(
        title="ms_test",
        lifespan=lifespan,
        root_path="/api"
    )
    app.state.container = container  # type: ignore[attr-defined]
    app.state.settings = settings  # type: ignore[attr-defined]

    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, generic_exception_handler)  # type: ignore[arg-type]

    app.include_router(rest_controller.router)

    return app


def start_server() -> None:
    """Launch uvicorn — called from the [project.scripts] entrypoint."""
    settings = Settings()
    uvicorn.run(
        "ms_test.application.app:create_app",
        host=getattr(settings, "HOST", "0.0.0.0"),
        port=int(getattr(settings, "PORT", 8000)),
        factory=True,
        reload=False,
    )


if __name__ == "__main__":
    start_server()
