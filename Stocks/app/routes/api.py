"""
API routes for the AI Stock Tracking Agent.

This module contains REST API endpoints for managing stocks,
viewing alerts, and system configuration.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import JSONResponse

from ..models.stock import Stock, StockAlert, StockPrice
from ..models.sms import SMSMessage
from ..services.stock_service import StockService
from ..services.sms_service import SMSService
from ..services.agent_service import AgentService
from ..services.scheduler_service import SchedulerService

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["api"])

# Service instances (in production, use dependency injection)
stock_service = StockService()
sms_service = SMSService()
agent_service = AgentService()
scheduler_service = SchedulerService()


@router.get("/stocks", response_model=List[Dict[str, Any]])
async def get_tracked_stocks():
    """
    Get list of all tracked stocks.
    
    Returns:
        List of tracked stock information
    """
    try:
        # In a real implementation, fetch from database
        # For now, return mock data
        mock_stocks = [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "current_price": 150.00,
                "change_percent": 2.5,
                "added_date": "2024-01-01T00:00:00Z"
            },
            {
                "symbol": "TSLA", 
                "name": "Tesla Inc.",
                "current_price": 200.00,
                "change_percent": -1.2,
                "added_date": "2024-01-01T00:00:00Z"
            }
        ]
        
        logger.info(f"Retrieved {len(mock_stocks)} tracked stocks")
        return mock_stocks
        
    except Exception as e:
        logger.error(f"Error getting tracked stocks: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/stocks/{symbol}")
async def add_stock(symbol: str = Path(..., description="Stock symbol to add")):
    """
    Add a stock to the tracking list.
    
    Args:
        symbol: Stock symbol to add
        
    Returns:
        Success message with stock information
    """
    try:
        symbol = symbol.upper()
        
        # Validate stock symbol
        is_valid = await stock_service.validate_stock_symbol(symbol)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid stock symbol: {symbol}")
        
        # Get stock information
        stock_info = await stock_service.get_stock_info(symbol)
        if not stock_info:
            raise HTTPException(status_code=404, detail=f"Stock not found: {symbol}")
        
        # In a real implementation, save to database
        logger.info(f"Stock {symbol} added to tracking list")
        
        return {
            "message": f"Stock {symbol} added successfully",
            "symbol": symbol,
            "name": stock_info.get("name", symbol),
            "added_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding stock {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/stocks/{symbol}")
async def remove_stock(symbol: str = Path(..., description="Stock symbol to remove")):
    """
    Remove a stock from the tracking list.
    
    Args:
        symbol: Stock symbol to remove
        
    Returns:
        Success message
    """
    try:
        symbol = symbol.upper()
        
        # In a real implementation, remove from database
        logger.info(f"Stock {symbol} removed from tracking list")
        
        return {
            "message": f"Stock {symbol} removed successfully",
            "symbol": symbol,
            "removed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error removing stock {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stocks/{symbol}/quote")
async def get_stock_quote(symbol: str = Path(..., description="Stock symbol")):
    """
    Get current quote for a specific stock.
    
    Args:
        symbol: Stock symbol
        
    Returns:
        Current stock quote information
    """
    try:
        symbol = symbol.upper()
        
        # Get stock quote
        quote = await stock_service.get_stock_quote(symbol)
        if not quote:
            raise HTTPException(status_code=404, detail=f"Quote not found for {symbol}")
        
        return {
            "symbol": quote.symbol,
            "price": float(quote.price),
            "change": float(quote.change),
            "change_percent": float(quote.change_percent),
            "volume": quote.volume,
            "high": float(quote.high),
            "low": float(quote.low),
            "open": float(quote.open_price),
            "previous_close": float(quote.previous_close),
            "timestamp": quote.timestamp.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting quote for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stocks/{symbol}/history")
async def get_stock_history(
    symbol: str = Path(..., description="Stock symbol"),
    days: int = Query(30, description="Number of days of history", ge=1, le=365)
):
    """
    Get historical price data for a stock.
    
    Args:
        symbol: Stock symbol
        days: Number of days of historical data
        
    Returns:
        List of historical price data
    """
    try:
        symbol = symbol.upper()
        
        # Get historical prices
        prices = await stock_service.get_historical_prices(symbol, days)
        
        # Convert to API format
        history = []
        for price in prices:
            history.append({
                "date": price.timestamp.isoformat(),
                "price": float(price.price),
                "volume": price.volume,
                "change": float(price.change) if price.change else None,
                "change_percent": float(price.change_percent) if price.change_percent else None
            })
        
        return {
            "symbol": symbol,
            "days": days,
            "data_points": len(history),
            "history": history
        }
        
    except Exception as e:
        logger.error(f"Error getting history for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/alerts", response_model=List[Dict[str, Any]])
async def get_alerts(
    limit: int = Query(50, description="Maximum number of alerts to return", ge=1, le=100),
    symbol: Optional[str] = Query(None, description="Filter by stock symbol")
):
    """
    Get list of stock alerts.
    
    Args:
        limit: Maximum number of alerts to return
        symbol: Optional stock symbol filter
        
    Returns:
        List of stock alerts
    """
    try:
        # In a real implementation, fetch from database
        # For now, return mock data
        mock_alerts = [
            {
                "id": 1,
                "symbol": "AAPL",
                "previous_price": 145.00,
                "current_price": 150.00,
                "change_percent": 3.45,
                "alert_message": "AAPL showed strong performance with positive market sentiment.",
                "news_summary": "Apple reported strong quarterly earnings.",
                "created_at": "2024-01-01T10:00:00Z",
                "sent_at": "2024-01-01T10:01:00Z",
                "is_sent": True
            }
        ]
        
        # Filter by symbol if provided
        if symbol:
            symbol = symbol.upper()
            mock_alerts = [alert for alert in mock_alerts if alert["symbol"] == symbol]
        
        # Limit results
        mock_alerts = mock_alerts[:limit]
        
        logger.info(f"Retrieved {len(mock_alerts)} alerts")
        return mock_alerts
        
    except Exception as e:
        logger.error(f"Error getting alerts: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/stocks/{symbol}/analyze")
async def analyze_stock_movement(
    symbol: str = Path(..., description="Stock symbol to analyze"),
    previous_price: float = Query(..., description="Previous price"),
    current_price: float = Query(..., description="Current price")
):
    """
    Analyze stock movement and generate AI insights.
    
    Args:
        symbol: Stock symbol
        previous_price: Previous price
        current_price: Current price
        
    Returns:
        AI analysis of the stock movement
    """
    try:
        symbol = symbol.upper()
        
        # Generate AI analysis
        analysis = await agent_service.analyze_stock_movement(
            symbol, previous_price, current_price
        )
        
        return {
            "symbol": analysis.symbol,
            "analysis": analysis.analysis,
            "confidence_score": analysis.confidence_score,
            "key_factors": analysis.key_factors,
            "recommendation": analysis.recommendation,
            "created_at": analysis.created_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing stock {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/sms/messages")
async def get_sms_messages(
    limit: int = Query(50, description="Maximum number of messages to return", ge=1, le=100),
    direction: Optional[str] = Query(None, description="Filter by direction (inbound/outbound)")
):
    """
    Get list of SMS messages.
    
    Args:
        limit: Maximum number of messages to return
        direction: Optional direction filter
        
    Returns:
        List of SMS messages
    """
    try:
        # In a real implementation, fetch from database
        # For now, return mock data
        mock_messages = [
            {
                "id": 1,
                "from_number": "+1234567890",
                "to_number": "+0987654321",
                "body": "Add AAPL",
                "direction": "inbound",
                "status": "received",
                "created_at": "2024-01-01T10:00:00Z"
            },
            {
                "id": 2,
                "from_number": "+0987654321",
                "to_number": "+1234567890", 
                "body": "AAPL added to your watchlist!",
                "direction": "outbound",
                "status": "sent",
                "created_at": "2024-01-01T10:00:01Z"
            }
        ]
        
        # Filter by direction if provided
        if direction:
            mock_messages = [msg for msg in mock_messages if msg["direction"] == direction]
        
        # Limit results
        mock_messages = mock_messages[:limit]
        
        logger.info(f"Retrieved {len(mock_messages)} SMS messages")
        return mock_messages
        
    except Exception as e:
        logger.error(f"Error getting SMS messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/sms/send")
async def send_sms(
    to_number: str = Query(..., description="Recipient phone number"),
    message: str = Query(..., description="Message content"),
    message_type: str = Query("text", description="Type of message")
):
    """
    Send an SMS message.
    
    Args:
        to_number: Recipient phone number
        message: Message content
        message_type: Type of message
        
    Returns:
        SMS sending result
    """
    try:
        # Send SMS
        sms_record = await sms_service.send_sms(to_number, message, message_type)
        
        if sms_record and sms_record.status == "sent":
            return {
                "success": True,
                "message": "SMS sent successfully",
                "twilio_sid": sms_record.twilio_sid,
                "sent_at": sms_record.sent_at.isoformat() if sms_record.sent_at else None
            }
        else:
            return {
                "success": False,
                "message": "Failed to send SMS",
                "error": sms_record.error_message if sms_record else "Unknown error"
            }
        
    except Exception as e:
        logger.error(f"Error sending SMS: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/scheduler/status")
async def get_scheduler_status():
    """
    Get scheduler status and configuration.
    
    Returns:
        Scheduler status information
    """
    try:
        status = scheduler_service.get_scheduler_status()
        return status
        
    except Exception as e:
        logger.error(f"Error getting scheduler status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/scheduler/tasks")
async def get_scheduled_tasks():
    """
    Get list of scheduled tasks.
    
    Returns:
        List of scheduled tasks
    """
    try:
        tasks = scheduler_service.get_scheduled_tasks()
        return {
            "tasks": tasks,
            "count": len(tasks)
        }
        
    except Exception as e:
        logger.error(f"Error getting scheduled tasks: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/scheduler/check-now")
async def trigger_immediate_check():
    """
    Trigger an immediate stock price check.
    
    Returns:
        Check execution result
    """
    try:
        success = await scheduler_service.execute_immediate_check()
        
        if success:
            return {
                "success": True,
                "message": "Stock check triggered successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "success": False,
                "message": "Failed to trigger stock check"
            }
        
    except Exception as e:
        logger.error(f"Error triggering immediate check: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
