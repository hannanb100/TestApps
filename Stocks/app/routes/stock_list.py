"""
Stock List API Routes - REST endpoints for managing tracked stocks.

This module provides API endpoints for adding, removing, updating,
and retrieving the list of stocks being monitored for price changes.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import JSONResponse

from ..models.stock_list import (
    StockListResponse, 
    StockListSummary,
    AddStockRequest,
    UpdateStockRequest
)
from ..services.stock_list_service import StockListService

# Configure logging
logger = logging.getLogger(__name__)

# Create router for stock list endpoints
router = APIRouter(prefix="/api/v1/stocks", tags=["stock-list"])

# Initialize the stock list service
stock_list_service = StockListService()


@router.get("/list", response_model=List[StockListResponse])
async def get_tracked_stocks():
    """
    Get all tracked stocks.
    
    Returns a list of all stocks that are being monitored for price changes,
    including their current settings and status.
    
    Returns:
        List of tracked stocks with detailed information
    """
    try:
        logger.info("Getting all tracked stocks")
        stocks = stock_list_service.get_all_stocks()
        
        return JSONResponse(
            status_code=200,
            content={
                "stocks": [stock.dict() for stock in stocks] if stocks else [],
                "count": len(stocks) if stocks else 0,
                "message": f"Retrieved {len(stocks)} tracked stocks"
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting tracked stocks: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve tracked stocks: {str(e)}"
        )


@router.get("/list/active", response_model=List[str])
async def get_active_stock_symbols():
    """
    Get list of active stock symbols.
    
    Returns a simple list of stock symbols that are currently
    being actively monitored for price changes.
    
    Returns:
        List of active stock symbols
    """
    try:
        logger.info("Getting active stock symbols")
        symbols = stock_list_service.get_active_stocks()
        
        return JSONResponse(
            status_code=200,
            content={
                "symbols": symbols,
                "count": len(symbols),
                "message": f"Retrieved {len(symbols)} active stock symbols"
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting active stock symbols: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve active stock symbols: {str(e)}"
        )


@router.get("/list/{stock_id}", response_model=StockListResponse)
async def get_tracked_stock(
    stock_id: int = Path(..., description="ID of the tracked stock to retrieve")
):
    """
    Get a specific tracked stock by ID.
    
    Returns detailed information about a specific stock that is
    being tracked, including its settings and current status.
    
    Args:
        stock_id: The ID of the tracked stock to retrieve
        
    Returns:
        Detailed information about the tracked stock
    """
    try:
        logger.info(f"Getting tracked stock with ID: {stock_id}")
        stock = stock_list_service.get_stock_by_id(stock_id)
        
        if not stock:
            raise HTTPException(
                status_code=404,
                detail=f"Tracked stock with ID {stock_id} not found"
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "stock": stock.dict() if stock else None,
                "message": f"Retrieved tracked stock {stock.symbol}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tracked stock {stock_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve tracked stock: {str(e)}"
        )


@router.post("/list", response_model=StockListResponse)
async def add_tracked_stock(request: AddStockRequest):
    """
    Add a new stock to the tracking list.
    
    Adds a new stock to be monitored for price changes and alerts.
    The stock symbol will be validated to ensure it exists.
    
    Args:
        request: AddStockRequest with stock information
        
    Returns:
        Information about the newly added tracked stock
    """
    try:
        logger.info(f"Adding new tracked stock: {request.symbol}")
        stock = stock_list_service.add_stock(request)
        
        if not stock:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to add stock {request.symbol}. Stock may already exist or be invalid."
            )
        
        return JSONResponse(
            status_code=201,
            content={
                "stock": stock.dict() if stock else None,
                "message": f"Successfully added {stock.symbol} to tracking list"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding tracked stock {request.symbol}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add tracked stock: {str(e)}"
        )


@router.put("/list/{stock_id}", response_model=StockListResponse)
async def update_tracked_stock(
    stock_id: int = Path(..., description="ID of the tracked stock to update"),
    request: UpdateStockRequest = None
):
    """
    Update an existing tracked stock.
    
    Updates the settings for a stock that is already being tracked,
    such as alert threshold, alert type, or active status.
    
    Args:
        stock_id: The ID of the tracked stock to update
        request: UpdateStockRequest with updated information
        
    Returns:
        Updated information about the tracked stock
    """
    try:
        logger.info(f"Updating tracked stock with ID: {stock_id}")
        stock = stock_list_service.update_stock(stock_id, request)
        
        if not stock:
            raise HTTPException(
                status_code=404,
                detail=f"Tracked stock with ID {stock_id} not found"
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "stock": stock.dict() if stock else None,
                "message": f"Successfully updated {stock.symbol}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tracked stock {stock_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update tracked stock: {str(e)}"
        )


@router.delete("/list/{stock_id}")
async def remove_tracked_stock(
    stock_id: int = Path(..., description="ID of the tracked stock to remove")
):
    """
    Remove a stock from the tracking list.
    
    Removes a stock from being monitored for price changes and alerts.
    This action cannot be undone.
    
    Args:
        stock_id: The ID of the tracked stock to remove
        
    Returns:
        Confirmation message
    """
    try:
        logger.info(f"Removing tracked stock with ID: {stock_id}")
        success = stock_list_service.remove_stock(stock_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Tracked stock with ID {stock_id} not found"
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Successfully removed tracked stock with ID {stock_id}",
                "success": True
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing tracked stock {stock_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to remove tracked stock: {str(e)}"
        )


@router.get("/list/summary", response_model=StockListSummary)
async def get_stock_list_summary():
    """
    Get a summary of the tracked stocks.
    
    Returns summary statistics about the tracked stocks including
    total count, active count, and average settings.
    
    Returns:
        Summary statistics about the tracked stocks
    """
    try:
        logger.info("Getting stock list summary")
        summary = stock_list_service.get_stock_list_summary()
        
        return JSONResponse(
            status_code=200,
            content={
                "summary": summary.dict() if summary else None,
                "message": "Stock list summary retrieved successfully"
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting stock list summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve stock list summary: {str(e)}"
        )


@router.get("/list/status")
async def get_stock_list_service_status():
    """
    Get the status of the stock list service.
    
    Returns information about the stock list service including
    storage file status and number of tracked stocks.
    
    Returns:
        Service status information
    """
    try:
        logger.info("Getting stock list service status")
        
        # Get basic statistics
        summary = stock_list_service.get_stock_list_summary()
        
        # Check storage file status
        import os
        storage_file = stock_list_service.storage_file
        file_exists = os.path.exists(storage_file)
        file_size = os.path.getsize(storage_file) if file_exists else 0
        
        status = {
            "service": "Stock List Service",
            "status": "operational",
            "storage_file": storage_file,
            "file_exists": file_exists,
            "file_size_bytes": file_size,
            "total_stocks": summary.total_stocks,
            "active_stocks": summary.active_stocks,
            "inactive_stocks": summary.inactive_stocks,
            "average_threshold": summary.average_threshold,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        return JSONResponse(
            status_code=200,
            content={
                "status": status,
                "message": "Stock list service status retrieved successfully"
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting stock list service status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve stock list service status: {str(e)}"
        )
