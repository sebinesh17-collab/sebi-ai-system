from __future__ import annotations

from fastapi import FastAPI

from config.settings import get_settings
from sebi.api.routes.requests import router as request_router
from sebi.api.routes.system import router as system_router
from sebi.monitoring.logging import configure_logging
from sebi.storage.files import ensure_directories


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level, settings.audit_log_path)
    ensure_directories(
        [
            settings.storage_root,
            settings.logs_root,
            settings.watch_root,
        ]
    )

    app = FastAPI(
        title="SEBI",
        version="0.1.0",
        description="Modular AI platform orchestrated by SEBIBrain.",
    )
    app.include_router(system_router)
    app.include_router(request_router)

    @app.get("/")
    def root() -> dict:
        return {
            "name": "SEBI",
            "brain": "SEBIBrain",
            "docs": "/docs",
        }

    return app


app = create_app()
