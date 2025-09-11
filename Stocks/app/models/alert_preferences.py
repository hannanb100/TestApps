"""
Alert Preferences Model - Manages user alert preferences and settings.

This module defines the data structure for storing user preferences
for alert thresholds, frequency, types, and other customization options.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator


class AlertPreferences(BaseModel):
    """
    Model for storing user alert preferences.
    
    This stores all the customizable settings that control how
    alerts are generated, sent, and managed.
    """
    
    # Unique identifier for these preferences
    id: Optional[int] = Field(None, description="Unique preferences ID")
    
    # Global alert settings
    global_alert_threshold: float = Field(
        default=1.0, 
        ge=0.1, 
        le=50.0, 
        description="Global alert threshold percentage (0.1-50.0)"
    )
    
    # Alert frequency settings
    alert_frequency: str = Field(
        default="MARKET_HOURS", 
        description="Alert frequency: MARKET_HOURS, DAILY, HOURLY, CUSTOM"
    )
    
    # Market hours settings
    market_hours_only: bool = Field(
        default=True, 
        description="Only send alerts during market hours (9:30 AM - 4:00 PM EST)"
    )
    
    # Alert type preferences (simplified - single alert type)
    # Removed alert_types field as we now use a single alert type
    
    # Email preferences
    email_alerts_enabled: bool = Field(default=True, description="Enable email alerts")
    email_rich_format: bool = Field(default=True, description="Use rich HTML email format")
    
    # SMS preferences (legacy, kept for compatibility)
    sms_alerts_enabled: bool = Field(default=False, description="Enable SMS alerts (legacy)")
    
    # Alert content preferences
    include_analysis: bool = Field(default=True, description="Include AI analysis in alerts")
    include_key_factors: bool = Field(default=True, description="Include key factors in alerts")
    include_price_history: bool = Field(default=False, description="Include price history in alerts")
    
    # Notification preferences
    max_alerts_per_day: int = Field(
        default=10, 
        ge=1, 
        le=100, 
        description="Maximum number of alerts to send per day"
    )
    
    alert_cooldown_minutes: int = Field(
        default=30, 
        ge=0, 
        le=1440, 
        description="Minimum minutes between alerts for the same stock"
    )
    
    # Advanced settings
    enable_volume_alerts: bool = Field(default=False, description="Enable volume-based alerts")
    volume_threshold_multiplier: float = Field(
        default=2.0, 
        ge=1.0, 
        le=10.0, 
        description="Volume threshold multiplier (e.g., 2.0 = 2x average volume)"
    )
    
    enable_news_alerts: bool = Field(default=True, description="Include news analysis in alerts")
    news_sentiment_threshold: float = Field(
        default=0.7, 
        ge=0.0, 
        le=1.0, 
        description="News sentiment threshold for alerts (0.0-1.0)"
    )
    
    # Custom schedule settings
    custom_schedule: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Custom alert schedule configuration"
    )
    
    # Metadata
    created_date: Union[datetime, str] = Field(default_factory=datetime.utcnow, description="When preferences were created")
    updated_date: Union[datetime, str] = Field(default_factory=datetime.utcnow, description="When preferences were last updated")
    is_active: bool = Field(default=True, description="Whether these preferences are active")
    
    @validator('created_date', 'updated_date', pre=True)
    def parse_datetime_fields(cls, v):
        """Parse datetime fields from string or datetime."""
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                return datetime.utcnow()
        return v
    
    class Config:
        """Pydantic configuration for the model."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AlertPreferencesResponse(BaseModel):
    """
    Response model for alert preferences API endpoints.
    
    This is used when returning alert preferences data to the user,
    with additional computed fields for better user experience.
    """
    
    # Basic preferences information
    id: int
    global_alert_threshold: float
    alert_frequency: str
    market_hours_only: bool
    alert_types: List[str]
    email_alerts_enabled: bool
    email_rich_format: bool
    sms_alerts_enabled: bool
    include_analysis: bool
    include_key_factors: bool
    include_price_history: bool
    max_alerts_per_day: int
    alert_cooldown_minutes: int
    enable_volume_alerts: bool
    volume_threshold_multiplier: float
    enable_news_alerts: bool
    news_sentiment_threshold: float
    custom_schedule: Optional[Dict[str, Any]]
    created_date: Union[datetime, str]
    updated_date: Union[datetime, str]
    is_active: bool
    
    @validator('created_date', 'updated_date', pre=True)
    def parse_datetime_fields(cls, v):
        """Parse datetime fields from string or datetime."""
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                return datetime.utcnow()
        return v
    
    # Computed fields for better user experience
    next_alert_time: Optional[Union[datetime, str]] = Field(None, description="When the next alert is scheduled")
    alerts_sent_today: int = Field(0, description="Number of alerts sent today")
    cooldown_active: bool = Field(False, description="Whether cooldown is currently active")
    
    @validator('next_alert_time', pre=True)
    def parse_next_alert_time(cls, v):
        """Parse next_alert_time from string or datetime."""
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                return None
        return v
    
    class Config:
        """Pydantic configuration for the response model."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class UpdateAlertPreferencesRequest(BaseModel):
    """
    Request model for updating alert preferences.
    
    This defines the fields that can be updated for alert preferences.
    """
    
    global_alert_threshold: Optional[float] = Field(None, ge=0.1, le=50.0, description="Global alert threshold percentage")
    alert_frequency: Optional[str] = Field(None, description="Alert frequency setting")
    market_hours_only: Optional[bool] = Field(None, description="Market hours only setting")
    alert_types: Optional[List[str]] = Field(None, description="Alert types to send")
    email_alerts_enabled: Optional[bool] = Field(None, description="Enable email alerts")
    email_rich_format: Optional[bool] = Field(None, description="Use rich HTML email format")
    sms_alerts_enabled: Optional[bool] = Field(None, description="Enable SMS alerts")
    include_analysis: Optional[bool] = Field(None, description="Include AI analysis in alerts")
    include_key_factors: Optional[bool] = Field(None, description="Include key factors in alerts")
    include_price_history: Optional[bool] = Field(None, description="Include price history in alerts")
    max_alerts_per_day: Optional[int] = Field(None, ge=1, le=100, description="Maximum alerts per day")
    alert_cooldown_minutes: Optional[int] = Field(None, ge=0, le=1440, description="Alert cooldown minutes")
    enable_volume_alerts: Optional[bool] = Field(None, description="Enable volume-based alerts")
    volume_threshold_multiplier: Optional[float] = Field(None, ge=1.0, le=10.0, description="Volume threshold multiplier")
    enable_news_alerts: Optional[bool] = Field(None, description="Include news analysis in alerts")
    news_sentiment_threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="News sentiment threshold")
    custom_schedule: Optional[Dict[str, Any]] = Field(None, description="Custom alert schedule")
    is_active: Optional[bool] = Field(None, description="Whether preferences are active")
    
    class Config:
        """Pydantic configuration for the request model."""
        schema_extra = {
            "example": {
                "global_alert_threshold": 2.5,
                "alert_frequency": "MARKET_HOURS",
                "market_hours_only": True,
                "alert_types": ["DAILY", "INTRADAY"],
                "email_alerts_enabled": True,
                "max_alerts_per_day": 15,
                "alert_cooldown_minutes": 45
            }
        }


class AlertPreferencesSummary(BaseModel):
    """
    Summary model for alert preferences statistics.
    
    This provides a quick overview of alert preferences and usage,
    useful for dashboard displays.
    """
    
    total_preferences: int = Field(..., description="Total number of preference sets")
    active_preferences: int = Field(..., description="Number of active preference sets")
    average_threshold: float = Field(..., description="Average alert threshold across all preferences")
    most_common_frequency: str = Field(..., description="Most commonly used alert frequency")
    email_enabled_count: int = Field(..., description="Number of preferences with email enabled")
    sms_enabled_count: int = Field(..., description="Number of preferences with SMS enabled")
    last_updated: Optional[datetime] = Field(None, description="When preferences were last updated")
    
    class Config:
        """Pydantic configuration for the summary model."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
