"""
Alert History API Routes - REST endpoints for accessing alert history.

This module provides API endpoints for retrieving alert history,
including recent alerts, alerts by symbol, and alert summaries.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from ..models.alert_history import AlertHistoryResponse, AlertHistorySummary
from ..services.alert_history_service import AlertHistoryService

# Configure logging
logger = logging.getLogger(__name__)

# Create router for alert history endpoints
router = APIRouter(prefix="/api/v1/alerts", tags=["alert-history"])

# Initialize the alert history service
alert_history_service = AlertHistoryService()


@router.get("/history", response_model=List[AlertHistoryResponse])
async def get_recent_alerts(limit: int = Query(10, ge=1, le=50, description="Number of recent alerts to return")):
    """
    Get recent alert history.
    
    Returns the most recent alerts with details about price changes,
    analysis, and timestamps.
    
    Args:
        limit: Maximum number of alerts to return (1-50)
        
    Returns:
        List of recent alerts with computed fields
    """
    try:
        logger.info(f"Getting recent alerts (limit: {limit})")
        alerts = alert_history_service.get_recent_alerts(limit=limit)
        
        return JSONResponse(
            status_code=200,
            content={
                "alerts": [alert.model_dump() for alert in alerts] if alerts else [],
                "count": len(alerts) if alerts else 0,
                "message": f"Retrieved {len(alerts)} recent alerts"
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting recent alerts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve alert history: {str(e)}"
        )


@router.get("/history/{symbol}", response_model=List[AlertHistoryResponse])
async def get_alerts_by_symbol(
    symbol: str,
    limit: int = Query(10, ge=1, le=50, description="Number of alerts to return")
):
    """
    Get alert history for a specific stock symbol.
    
    Returns alerts for the specified stock symbol, sorted by most recent first.
    
    Args:
        symbol: Stock symbol to filter by (e.g., AAPL, TSLA)
        limit: Maximum number of alerts to return (1-50)
        
    Returns:
        List of alerts for the specified symbol
    """
    try:
        # Validate symbol format
        symbol = symbol.upper().strip()
        if not symbol or len(symbol) > 10:
            raise HTTPException(
                status_code=400,
                detail="Invalid stock symbol format"
            )
        
        logger.info(f"Getting alerts for symbol: {symbol} (limit: {limit})")
        alerts = alert_history_service.get_alerts_by_symbol(symbol=symbol, limit=limit)
        
        return JSONResponse(
            status_code=200,
            content={
                "symbol": symbol,
                "alerts": [alert.model_dump() for alert in alerts] if alerts else [],
                "count": len(alerts) if alerts else 0,
                "message": f"Retrieved {len(alerts)} alerts for {symbol}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alerts for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve alerts for {symbol}: {str(e)}"
        )


@router.get("/summary", response_model=AlertHistorySummary)
async def get_alert_summary():
    """
    Get alert history summary statistics.
    
    Returns summary information about alert activity including
    total alerts, alerts today, most active stock, and averages.
    
    Returns:
        Summary statistics about alert history
    """
    try:
        logger.info("Getting alert history summary")
        summary = alert_history_service.get_alert_summary()
        
        return JSONResponse(
            status_code=200,
            content={
                "summary": summary.model_dump() if summary else None,
                "message": "Alert history summary retrieved successfully"
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting alert summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve alert summary: {str(e)}"
        )


@router.delete("/history")
async def clear_alert_history():
    """
    Clear all alert history.
    
    WARNING: This will permanently delete all stored alert history.
    Use with caution!
    
    Returns:
        Confirmation message
    """
    try:
        logger.warning("Clearing all alert history")
        success = alert_history_service.clear_history()
        
        if success:
            return JSONResponse(
                status_code=200,
                content={
                    "message": "Alert history cleared successfully",
                    "success": True
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to clear alert history"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing alert history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear alert history: {str(e)}"
        )


@router.get("/status")
async def get_alert_service_status():
    """
    Get the status of the alert history service.
    
    Returns information about the alert history service including
    storage file status and number of stored alerts.
    
    Returns:
        Service status information
    """
    try:
        logger.info("Getting alert history service status")
        
        # Get basic statistics
        summary = alert_history_service.get_alert_summary()
        
        # Check storage file status
        import os
        storage_file = alert_history_service.storage_file
        file_exists = os.path.exists(storage_file)
        file_size = os.path.getsize(storage_file) if file_exists else 0
        
        status = {
            "service": "Alert History Service",
            "status": "operational",
            "storage_file": storage_file,
            "file_exists": file_exists,
            "file_size_bytes": file_size,
            "total_alerts": summary.total_alerts,
            "alerts_today": summary.alerts_today,
            "last_alert_time": summary.last_alert_time,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        return JSONResponse(
            status_code=200,
            content={
                "status": status,
                "message": "Alert history service status retrieved successfully"
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting alert service status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve alert service status: {str(e)}"
        )
