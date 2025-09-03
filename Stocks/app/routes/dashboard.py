"""
Dashboard Routes - Web interface for the AI Stock Tracking Agent.

This module provides web routes for the dashboard interface,
allowing users to view alert history and system status.
"""

import logging
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

# Configure logging
logger = logging.getLogger(__name__)

# Create router for dashboard endpoints
router = APIRouter(tags=["dashboard"])

# Set up templates directory
templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=templates_dir)


@router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """
    Serve the main dashboard page.
    
    This is the main web interface for viewing alert history,
    system status, and interacting with the stock monitoring system.
    
    Args:
        request: FastAPI request object
        
    Returns:
        HTML response with the dashboard page
    """
    try:
        logger.info("Serving dashboard home page")
        
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "title": "AI Stock Tracking Agent - Dashboard"
            }
        )
        
    except Exception as e:
        logger.error(f"Error serving dashboard: {str(e)}")
        return HTMLResponse(
            content=f"""
            <html>
                <head><title>Error</title></head>
                <body>
                    <h1>Error Loading Dashboard</h1>
                    <p>There was an error loading the dashboard: {str(e)}</p>
                    <p>Please check the server logs for more details.</p>
                </body>
            </html>
            """,
            status_code=500
        )


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_redirect(request: Request):
    """
    Redirect to the main dashboard.
    
    This provides an alternative URL for accessing the dashboard.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Redirect to the main dashboard
    """
    return await dashboard_home(request)
