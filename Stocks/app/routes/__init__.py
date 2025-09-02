"""
Routes package for the AI Stock Tracking Agent.

This package contains all FastAPI route handlers including
webhooks, API endpoints, and health checks.
"""

from .webhooks import router as webhooks_router
from .api import router as api_router
from .health import router as health_router

__all__ = [
    "webhooks_router",
    "api_router", 
    "health_router"
]
