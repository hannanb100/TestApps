"""
Stock List Model - Manages the list of tracked stocks.

This module defines the data structure for managing the list of stocks
that are being monitored for price changes and alerts.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class TrackedStock(BaseModel):
    """
    Model for a single tracked stock.
    
    This represents one stock that is being monitored for price changes
    and will trigger alerts when the price moves beyond the threshold.
    """
    
    # Unique identifier for this tracked stock
    id: Optional[int] = Field(None, description="Unique stock ID")
    
    # Stock information
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL, TSLA)")
    name: Optional[str] = Field(None, description="Company name (e.g., Apple Inc.)")
    
    # Tracking settings
    added_date: datetime = Field(default_factory=datetime.utcnow, description="When this stock was added to tracking")
    is_active: bool = Field(default=True, description="Whether this stock is actively being monitored")
    
    # Alert preferences (can be customized per stock)
    alert_threshold: float = Field(default=3.0, description="Price change threshold for alerts (percentage)")
    alert_type: str = Field(default="BOTH", description="Alert type: DAILY, INTRADAY, or BOTH")
    
    # Additional metadata
    notes: Optional[str] = Field(None, description="User notes about this stock")
    
    class Config:
        """Pydantic configuration for the model."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StockListResponse(BaseModel):
    """
    Response model for stock list API endpoints.
    
    This is used when returning stock list data to the user,
    with additional computed fields for better user experience.
    """
    
    # Basic stock information
    id: int
    symbol: str
    name: Optional[str]
    added_date: datetime
    is_active: bool
    alert_threshold: float
    alert_type: str
    notes: Optional[str]
    
    # Computed fields for better user experience
    days_tracked: int = Field(..., description="Number of days this stock has been tracked")
    current_price: Optional[float] = Field(None, description="Current stock price (if available)")
    last_alert: Optional[datetime] = Field(None, description="When the last alert was sent for this stock")
    
    class Config:
        """Pydantic configuration for the response model."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class StockListSummary(BaseModel):
    """
    Summary model for stock list statistics.
    
    This provides a quick overview of the tracked stocks,
    useful for dashboard displays.
    """
    
    total_stocks: int = Field(..., description="Total number of tracked stocks")
    active_stocks: int = Field(..., description="Number of actively monitored stocks")
    inactive_stocks: int = Field(..., description="Number of inactive stocks")
    most_recent_addition: Optional[datetime] = Field(None, description="When the most recent stock was added")
    average_threshold: float = Field(..., description="Average alert threshold across all stocks")
    
    class Config:
        """Pydantic configuration for the summary model."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class AddStockRequest(BaseModel):
    """
    Request model for adding a new stock to the tracking list.
    
    This defines the required and optional fields when adding
    a new stock to be monitored.
    """
    
    symbol: str = Field(..., description="Stock symbol to add (e.g., AAPL, TSLA)")
    name: Optional[str] = Field(None, description="Company name (optional, will be fetched if not provided)")
    alert_threshold: float = Field(default=3.0, ge=0.1, le=50.0, description="Alert threshold percentage (0.1-50.0)")
    alert_type: str = Field(default="BOTH", description="Alert type: DAILY, INTRADAY, or BOTH")
    notes: Optional[str] = Field(None, description="Optional notes about this stock")
    
    class Config:
        """Pydantic configuration for the request model."""
        schema_extra = {
            "example": {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "alert_threshold": 3.0,
                "alert_type": "BOTH",
                "notes": "Tech giant, watch for earnings announcements"
            }
        }


class UpdateStockRequest(BaseModel):
    """
    Request model for updating an existing tracked stock.
    
    This defines the fields that can be updated for a stock
    that is already being tracked.
    """
    
    name: Optional[str] = Field(None, description="Company name")
    is_active: Optional[bool] = Field(None, description="Whether to actively monitor this stock")
    alert_threshold: Optional[float] = Field(None, ge=0.1, le=50.0, description="Alert threshold percentage")
    alert_type: Optional[str] = Field(None, description="Alert type: DAILY, INTRADAY, or BOTH")
    notes: Optional[str] = Field(None, description="Notes about this stock")
    
    class Config:
        """Pydantic configuration for the request model."""
        schema_extra = {
            "example": {
                "name": "Apple Inc.",
                "is_active": True,
                "alert_threshold": 2.5,
                "alert_type": "DAILY",
                "notes": "Updated notes about Apple"
            }
        }
