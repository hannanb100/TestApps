"""
User-related Pydantic models.

This module contains models for user data, preferences,
and settings management.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


class User(BaseModel):
    """
    Model representing a user of the stock tracking system.
    
    This model stores user information and basic settings.
    Currently designed for single-user system but extensible.
    """
    
    id: Optional[int] = Field(None, description="User ID")
    phone_number: str = Field(..., description="User's phone number")
    name: Optional[str] = Field(None, description="User's name")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Account creation time")
    last_active: Optional[datetime] = Field(None, description="Last activity timestamp")
    is_active: bool = Field(default=True, description="Whether user account is active")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format."""
        if not v or not isinstance(v, str):
            raise ValueError("Phone number must be a non-empty string")
        # Basic phone number validation (can be enhanced)
        cleaned = ''.join(filter(str.isdigit, v))
        if len(cleaned) < 10:
            raise ValueError("Phone number must have at least 10 digits")
        return v


class UserPreferences(BaseModel):
    """
    Model for user preferences and settings.
    
    This model stores user-specific configuration options
    for the stock tracking system.
    """
    
    user_id: int = Field(..., description="Associated user ID")
    alert_threshold_percent: Decimal = Field(
        default=Decimal("5.0"), 
        description="Default alert threshold percentage"
    )
    check_interval_minutes: int = Field(
        default=60, 
        description="Default check interval in minutes"
    )
    max_stocks: int = Field(
        default=20, 
        description="Maximum number of stocks to track"
    )
    enable_news_summaries: bool = Field(
        default=True, 
        description="Whether to include news summaries in alerts"
    )
    enable_ai_analysis: bool = Field(
        default=True, 
        description="Whether to include AI analysis in alerts"
    )
    timezone: str = Field(
        default="UTC", 
        description="User's timezone"
    )
    language: str = Field(
        default="en", 
        description="Preferred language for alerts"
    )
    alert_frequency: str = Field(
        default="immediate", 
        description="Alert frequency: immediate, daily, weekly"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Preferences creation time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    
    @validator('alert_threshold_percent')
    def validate_threshold(cls, v):
        """Validate alert threshold."""
        if v <= 0:
            raise ValueError("Alert threshold must be positive")
        if v > 100:
            raise ValueError("Alert threshold cannot exceed 100%")
        return v
    
    @validator('check_interval_minutes')
    def validate_interval(cls, v):
        """Validate check interval."""
        if v < 1:
            raise ValueError("Check interval must be at least 1 minute")
        if v > 1440:  # 24 hours
            raise ValueError("Check interval cannot exceed 24 hours")
        return v
    
    @validator('max_stocks')
    def validate_max_stocks(cls, v):
        """Validate maximum stocks."""
        if v < 1:
            raise ValueError("Must allow at least 1 stock")
        if v > 100:
            raise ValueError("Cannot track more than 100 stocks")
        return v


class UserSession(BaseModel):
    """
    Model for user session tracking.
    
    This model tracks user sessions and activity for
    analytics and debugging purposes.
    """
    
    id: Optional[int] = Field(None, description="Session ID")
    user_id: int = Field(..., description="Associated user ID")
    session_token: str = Field(..., description="Session token")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Session start time")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="Last activity time")
    is_active: bool = Field(default=True, description="Whether session is active")
    ip_address: Optional[str] = Field(None, description="User's IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")


class UserActivity(BaseModel):
    """
    Model for tracking user activities.
    
    This model logs user actions for analytics and
    system improvement.
    """
    
    id: Optional[int] = Field(None, description="Activity ID")
    user_id: int = Field(..., description="Associated user ID")
    activity_type: str = Field(..., description="Type of activity (add_stock, remove_stock, etc.)")
    activity_data: Dict[str, Any] = Field(default_factory=dict, description="Activity-specific data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Activity timestamp")
    success: bool = Field(default=True, description="Whether activity was successful")
    error_message: Optional[str] = Field(None, description="Error message if activity failed")


class UserStats(BaseModel):
    """
    Model for user statistics and metrics.
    
    This model provides aggregated statistics about
    user activity and system usage.
    """
    
    user_id: int = Field(..., description="Associated user ID")
    total_stocks_tracked: int = Field(default=0, description="Total stocks ever tracked")
    current_stocks_tracked: int = Field(default=0, description="Currently tracked stocks")
    total_alerts_received: int = Field(default=0, description="Total alerts received")
    total_sms_sent: int = Field(default=0, description="Total SMS messages sent")
    average_response_time: Optional[float] = Field(None, description="Average response time in seconds")
    most_tracked_stock: Optional[str] = Field(None, description="Most frequently tracked stock")
    last_alert_date: Optional[datetime] = Field(None, description="Date of last alert")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Stats creation time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last stats update")
