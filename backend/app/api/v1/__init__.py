"""API v1 routes."""
from .auth import router as auth_router
from .datasets import router as datasets_router
from .uploads import router as uploads_router
from .jobs import router as jobs_router

__all__ = ["auth_router", "datasets_router", "uploads_router", "jobs_router"]
