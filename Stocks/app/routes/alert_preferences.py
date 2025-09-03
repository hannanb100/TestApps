"""
Alert Preferences API Routes - REST endpoints for managing alert preferences.

This module provides API endpoints for retrieving, updating, and managing
user alert preferences including thresholds, frequency, and notification settings.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ..models.alert_preferences import (
    AlertPreferencesResponse, 
    AlertPreferencesSummary,
    UpdateAlertPreferencesRequest
)
from ..services.alert_preferences_service import AlertPreferencesService

# Configure logging
logger = logging.getLogger(__name__)

# Create router for alert preferences endpoints
router = APIRouter(prefix="/api/v1/preferences", tags=["alert-preferences"])

# Initialize the alert preferences service
preferences_service = AlertPreferencesService()


@router.get("/alerts", response_model=AlertPreferencesResponse)
async def get_alert_preferences():
    """
    Get current alert preferences.
    
    Returns the current alert preferences including thresholds,
    frequency settings, notification preferences, and computed fields.
    
    Returns:
        Current alert preferences with computed fields
    """
    try:
        logger.info("Getting alert preferences")
        preferences = preferences_service.get_preferences()
        
        if not preferences:
            raise HTTPException(
                status_code=404,
                detail="Alert preferences not found"
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "preferences": preferences.model_dump() if preferences else None,
                "message": "Alert preferences retrieved successfully"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alert preferences: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve alert preferences: {str(e)}"
        )


@router.put("/alerts", response_model=AlertPreferencesResponse)
async def update_alert_preferences(request: UpdateAlertPreferencesRequest):
    """
    Update alert preferences.
    
    Updates the alert preferences with the provided settings.
    Only the fields provided in the request will be updated.
    
    Args:
        request: UpdateAlertPreferencesRequest with updated settings
        
    Returns:
        Updated alert preferences
    """
    try:
        logger.info("Updating alert preferences")
        preferences = preferences_service.update_preferences(request)
        
        if not preferences:
            raise HTTPException(
                status_code=400,
                detail="Failed to update alert preferences"
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "preferences": preferences.model_dump() if preferences else None,
                "message": "Alert preferences updated successfully"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating alert preferences: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update alert preferences: {str(e)}"
        )


@router.post("/alerts/reset", response_model=AlertPreferencesResponse)
async def reset_alert_preferences():
    """
    Reset alert preferences to default values.
    
    Resets all alert preferences to their default values.
    This action cannot be undone.
    
    Returns:
        Alert preferences with default values
    """
    try:
        logger.info("Resetting alert preferences to defaults")
        preferences = preferences_service.reset_to_defaults()
        
        if not preferences:
            raise HTTPException(
                status_code=500,
                detail="Failed to reset alert preferences"
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "preferences": preferences.model_dump() if preferences else None,
                "message": "Alert preferences reset to defaults successfully"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting alert preferences: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset alert preferences: {str(e)}"
        )


@router.get("/alerts/summary", response_model=AlertPreferencesSummary)
async def get_alert_preferences_summary():
    """
    Get alert preferences summary.
    
    Returns summary statistics about alert preferences including
    usage counts and common settings.
    
    Returns:
        Summary statistics about alert preferences
    """
    try:
        logger.info("Getting alert preferences summary")
        summary = preferences_service.get_preferences_summary()
        
        return JSONResponse(
            status_code=200,
            content={
                "summary": summary.model_dump() if summary else None,
                "message": "Alert preferences summary retrieved successfully"
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting alert preferences summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve alert preferences summary: {str(e)}"
        )


@router.get("/alerts/threshold")
async def get_effective_threshold(stock_symbol: Optional[str] = None):
    """
    Get the effective alert threshold for a stock.
    
    Returns the effective alert threshold that will be used for
    the specified stock, taking into account global and per-stock settings.
    
    Args:
        stock_symbol: Stock symbol (optional, for future per-stock thresholds)
        
    Returns:
        Effective alert threshold percentage
    """
    try:
        logger.info(f"Getting effective threshold for {stock_symbol or 'global'}")
        threshold = preferences_service.get_effective_threshold(stock_symbol)
        
        return JSONResponse(
            status_code=200,
            content={
                "stock_symbol": stock_symbol,
                "effective_threshold": threshold,
                "message": f"Effective threshold: {threshold}%"
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting effective threshold: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve effective threshold: {str(e)}"
        )


@router.post("/alerts/check")
async def check_alert_eligibility(stock_symbol: str, alert_type: str):
    """
    Check if an alert should be sent for a stock.
    
    Checks if an alert should be sent based on current preferences,
    including cooldown periods, daily limits, and alert type settings.
    
    Args:
        stock_symbol: Stock symbol to check
        alert_type: Type of alert (DAILY, INTRADAY, etc.)
        
    Returns:
        Whether the alert should be sent
    """
    try:
        logger.info(f"Checking alert eligibility for {stock_symbol} ({alert_type})")
        should_send = preferences_service.should_send_alert(stock_symbol, alert_type)
        
        return JSONResponse(
            status_code=200,
            content={
                "stock_symbol": stock_symbol,
                "alert_type": alert_type,
                "should_send": should_send,
                "message": f"Alert {'should' if should_send else 'should not'} be sent"
            }
        )
        
    except Exception as e:
        logger.error(f"Error checking alert eligibility: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check alert eligibility: {str(e)}"
        )


@router.get("/alerts/status")
async def get_alert_preferences_service_status():
    """
    Get the status of the alert preferences service.
    
    Returns information about the alert preferences service including
    storage file status and current preferences state.
    
    Returns:
        Service status information
    """
    try:
        logger.info("Getting alert preferences service status")
        
        # Get basic statistics
        summary = preferences_service.get_preferences_summary()
        
        # Check storage file status
        import os
        storage_file = preferences_service.storage_file
        file_exists = os.path.exists(storage_file)
        file_size = os.path.getsize(storage_file) if file_exists else 0
        
        # Get current preferences
        current_preferences = preferences_service.get_preferences()
        
        status = {
            "service": "Alert Preferences Service",
            "status": "operational",
            "storage_file": storage_file,
            "file_exists": file_exists,
            "file_size_bytes": file_size,
            "preferences_loaded": current_preferences is not None,
            "total_preferences": summary.total_preferences,
            "active_preferences": summary.active_preferences,
            "average_threshold": summary.average_threshold,
            "last_updated": summary.last_updated,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        return JSONResponse(
            status_code=200,
            content={
                "status": status,
                "message": "Alert preferences service status retrieved successfully"
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting alert preferences service status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve alert preferences service status: {str(e)}"
        )
