"""FastAPI application factory for DataMind-King."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.logging import setup_logging
from app.core.middleware import RequestIdMiddleware, TimingMiddleware
from app.core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    """Application lifespan: startup and shutdown hooks."""
    setup_logging()
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        description="World's most advanced AI Data Analyst platform",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        max_age=600,
    )

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "healthy", "version": "0.1.0", "env": settings.app_env}

    @app.get("/", tags=["root"])
    async def root() -> dict[str, str]:
        return {"message": "DataMind-King API"}

    # Routers are mounted in separate imports below once they exist
    from app.api.v1 import auth, datasets, uploads, jobs, agents, reports, dashboards, bi
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(datasets.router, prefix="/api/v1/datasets", tags=["datasets"])
    app.include_router(uploads.router, prefix="/api/v1/uploads", tags=["uploads"])
    app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
    app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
    app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
    app.include_router(dashboards.router, prefix="/api/v1/dashboards", tags=["dashboards"])
    app.include_router(bi.router, prefix="/api/v1/bi", tags=["bi"])

    return app


app = create_app()
