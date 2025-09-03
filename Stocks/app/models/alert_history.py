"""
Alert History Model - Stores information about sent alerts.

This module defines the data structure for storing alert history,
including when alerts were sent, what stocks triggered them, and
the analysis that was generated.
"""

from datetime import datetime
from typing import Optional, List, Union
from pydantic import BaseModel, Field, validator


class AlertHistory(BaseModel):
    """
    Model for storing alert history information.
    
    This stores details about each alert that was sent, including
    the stock symbol, price changes, analysis, and timestamp.
    """
    
    # Unique identifier for this alert
    id: Optional[int] = Field(None, description="Unique alert ID")
    
    # Stock information
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL, TSLA)")
    current_price: float = Field(..., description="Current stock price when alert was sent")
    previous_price: float = Field(..., description="Previous price (for comparison)")
    change_percent: float = Field(..., description="Percentage change that triggered the alert")
    
    # Alert details
    alert_type: str = Field(..., description="Type of alert (DAILY, INTRADAY)")
    analysis: str = Field(..., description="AI-generated analysis of the price movement")
    key_factors: List[str] = Field(default_factory=list, description="Key factors that influenced the price change")
    
    # Timestamp information
    timestamp: Union[datetime, str] = Field(default_factory=datetime.utcnow, description="When the alert was sent")
    
    @validator('timestamp', pre=True)
    def parse_timestamp(cls, v):
        """Parse timestamp from string or datetime."""
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                return datetime.utcnow()
        return v
    
    # Additional metadata
    threshold_used: float = Field(..., description="Alert threshold that was used (e.g., 3.0 for 3%)")
    email_sent: bool = Field(default=True, description="Whether email was successfully sent")
    
    class Config:
        """Pydantic configuration for the model."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AlertHistoryResponse(BaseModel):
    """
    Response model for alert history API endpoints.
    
    This is used when returning alert history data to the user,
    with additional computed fields for better user experience.
    """
    
    # Basic alert information
    id: int
    symbol: str
    current_price: float
    previous_price: float
    change_percent: float
    alert_type: str
    analysis: str
    key_factors: List[str]
    timestamp: datetime
    threshold_used: float
    email_sent: bool
    
    # Computed fields for better user experience
    price_change_dollar: float = Field(..., description="Dollar amount change (computed)")
    time_ago: str = Field(..., description="Human-readable time ago (e.g., '2 hours ago')")
    
    class Config:
        """Pydantic configuration for the response model."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AlertHistorySummary(BaseModel):
    """
    Summary model for alert history statistics.
    
    This provides a quick overview of alert activity,
    useful for dashboard displays.
    """
    
    total_alerts: int = Field(..., description="Total number of alerts sent")
    alerts_today: int = Field(..., description="Number of alerts sent today")
    most_active_stock: str = Field(..., description="Stock with most alerts")
    last_alert_time: Optional[datetime] = Field(None, description="When the last alert was sent")
    average_change_percent: float = Field(..., description="Average percentage change across all alerts")
    
    class Config:
        """Pydantic configuration for the summary model."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
