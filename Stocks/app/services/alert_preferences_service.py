"""
Alert Preferences Service - Manages user alert preferences and settings.

This service handles storing, retrieving, and updating user preferences
for alert thresholds, frequency, types, and other customization options.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import os

from ..models.alert_preferences import (
    AlertPreferences, 
    AlertPreferencesResponse, 
    AlertPreferencesSummary,
    UpdateAlertPreferencesRequest
)

# Configure logging
logger = logging.getLogger(__name__)


class AlertPreferencesService:
    """
    Service for managing alert preferences.
    
    This service stores preferences in a simple JSON file
    for now, but could be easily upgraded to use a database later.
    """
    
    def __init__(self, storage_file: str = "alert_preferences.json"):
        """
        Initialize the alert preferences service.
        
        Args:
            storage_file: Path to the JSON file for storing preferences
        """
        self.storage_file = storage_file
        self.preferences: Optional[AlertPreferences] = None
        self._load_preferences()
        logger.info(f"AlertPreferencesService initialized with preferences: {self.preferences is not None}")
    
    def _load_preferences(self):
        """Load existing preferences from the storage file."""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.preferences = AlertPreferences(**data)
                logger.info(f"Loaded alert preferences from {self.storage_file}")
            else:
                # Initialize with default preferences if no file exists
                self._initialize_default_preferences()
                logger.info(f"No existing preferences file found, initialized with default preferences")
        except Exception as e:
            logger.error(f"Error loading alert preferences: {str(e)}")
            self._initialize_default_preferences()
    
    def _initialize_default_preferences(self):
        """Initialize with default alert preferences."""
        self.preferences = AlertPreferences(
            id=1,
            global_alert_threshold=3.0,
            alert_frequency="MARKET_HOURS",
            market_hours_only=True,
            alert_types=["DAILY", "INTRADAY"],
            email_alerts_enabled=True,
            email_rich_format=True,
            sms_alerts_enabled=False,
            include_analysis=True,
            include_key_factors=True,
            include_price_history=False,
            max_alerts_per_day=10,
            alert_cooldown_minutes=30,
            enable_volume_alerts=False,
            volume_threshold_multiplier=2.0,
            enable_news_alerts=True,
            news_sentiment_threshold=0.7,
            custom_schedule=None,
            created_date=datetime.utcnow(),
            updated_date=datetime.utcnow(),
            is_active=True
        )
        self._save_preferences()
    
    def _save_preferences(self):
        """Save preferences to the storage file."""
        try:
            if self.preferences:
                preferences_data = self.preferences.model_dump()
                
                with open(self.storage_file, 'w') as f:
                    json.dump(preferences_data, f, indent=2, default=str)
                
                logger.info(f"Saved alert preferences to {self.storage_file}")
        except Exception as e:
            logger.error(f"Error saving alert preferences: {str(e)}")
    
    def get_preferences(self) -> Optional[AlertPreferencesResponse]:
        """
        Get current alert preferences with computed fields.
        
        Returns:
            AlertPreferencesResponse with computed fields, or None if no preferences
        """
        try:
            if not self.preferences:
                logger.warning("No alert preferences found")
                return None
            
            # Calculate computed fields
            next_alert_time = self._calculate_next_alert_time()
            alerts_sent_today = self._get_alerts_sent_today()
            cooldown_active = self._is_cooldown_active()
            
            response = AlertPreferencesResponse(
                id=self.preferences.id,
                global_alert_threshold=self.preferences.global_alert_threshold,
                alert_frequency=self.preferences.alert_frequency,
                market_hours_only=self.preferences.market_hours_only,
                alert_types=self.preferences.alert_types,
                email_alerts_enabled=self.preferences.email_alerts_enabled,
                email_rich_format=self.preferences.email_rich_format,
                sms_alerts_enabled=self.preferences.sms_alerts_enabled,
                include_analysis=self.preferences.include_analysis,
                include_key_factors=self.preferences.include_key_factors,
                include_price_history=self.preferences.include_price_history,
                max_alerts_per_day=self.preferences.max_alerts_per_day,
                alert_cooldown_minutes=self.preferences.alert_cooldown_minutes,
                enable_volume_alerts=self.preferences.enable_volume_alerts,
                volume_threshold_multiplier=self.preferences.volume_threshold_multiplier,
                enable_news_alerts=self.preferences.enable_news_alerts,
                news_sentiment_threshold=self.preferences.news_sentiment_threshold,
                custom_schedule=self.preferences.custom_schedule,
                created_date=self.preferences.created_date.isoformat() if isinstance(self.preferences.created_date, datetime) else self.preferences.created_date,
                updated_date=self.preferences.updated_date.isoformat() if isinstance(self.preferences.updated_date, datetime) else self.preferences.updated_date,
                is_active=self.preferences.is_active,
                next_alert_time=next_alert_time.isoformat() if isinstance(next_alert_time, datetime) else next_alert_time,
                alerts_sent_today=alerts_sent_today,
                cooldown_active=cooldown_active
            )
            
            logger.info("Retrieved alert preferences with computed fields")
            return response
            
        except Exception as e:
            logger.error(f"Error getting alert preferences: {str(e)}")
            return None
    
    def update_preferences(self, request: UpdateAlertPreferencesRequest) -> Optional[AlertPreferencesResponse]:
        """
        Update alert preferences.
        
        Args:
            request: UpdateAlertPreferencesRequest with updated information
            
        Returns:
            AlertPreferencesResponse if successful, None if failed
        """
        try:
            if not self.preferences:
                logger.error("No existing preferences to update")
                return None
            
            # Update fields if provided
            update_data = request.dict(exclude_unset=True)
            
            for field, value in update_data.items():
                if hasattr(self.preferences, field):
                    setattr(self.preferences, field, value)
            
            # Update the updated_date
            self.preferences.updated_date = datetime.utcnow()
            
            # Save to file
            self._save_preferences()
            
            logger.info("Updated alert preferences")
            
            # Return updated response
            return self.get_preferences()
            
        except Exception as e:
            logger.error(f"Error updating alert preferences: {str(e)}")
            return None
    
    def reset_to_defaults(self) -> Optional[AlertPreferencesResponse]:
        """
        Reset preferences to default values.
        
        Returns:
            AlertPreferencesResponse with default preferences
        """
        try:
            self._initialize_default_preferences()
            logger.info("Reset alert preferences to defaults")
            return self.get_preferences()
            
        except Exception as e:
            logger.error(f"Error resetting preferences to defaults: {str(e)}")
            return None
    
    def get_preferences_summary(self) -> AlertPreferencesSummary:
        """
        Get a summary of alert preferences.
        
        Returns:
            Summary statistics about alert preferences
        """
        try:
            if not self.preferences:
                return AlertPreferencesSummary(
                    total_preferences=0,
                    active_preferences=0,
                    average_threshold=0.0,
                    most_common_frequency="MARKET_HOURS",
                    email_enabled_count=0,
                    sms_enabled_count=0,
                    last_updated=None
                )
            
            summary = AlertPreferencesSummary(
                total_preferences=1,
                active_preferences=1 if self.preferences.is_active else 0,
                average_threshold=self.preferences.global_alert_threshold,
                most_common_frequency=self.preferences.alert_frequency,
                email_enabled_count=1 if self.preferences.email_alerts_enabled else 0,
                sms_enabled_count=1 if self.preferences.sms_alerts_enabled else 0,
                last_updated=self.preferences.updated_date
            )
            
            logger.info("Generated alert preferences summary")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating preferences summary: {str(e)}")
            return AlertPreferencesSummary(
                total_preferences=0,
                active_preferences=0,
                average_threshold=0.0,
                most_common_frequency="MARKET_HOURS",
                email_enabled_count=0,
                sms_enabled_count=0,
                last_updated=None
            )
    
    def _calculate_next_alert_time(self) -> Optional[datetime]:
        """
        Calculate when the next alert is scheduled.
        
        Returns:
            Next alert time, or None if not applicable
        """
        try:
            if not self.preferences or not self.preferences.is_active:
                return None
            
            now = datetime.utcnow()
            
            # Simple calculation based on alert frequency
            if self.preferences.alert_frequency == "HOURLY":
                return now + timedelta(hours=1)
            elif self.preferences.alert_frequency == "DAILY":
                return now + timedelta(days=1)
            elif self.preferences.alert_frequency == "MARKET_HOURS":
                # Next market open (simplified)
                return now + timedelta(hours=1)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error calculating next alert time: {str(e)}")
            return None
    
    def _get_alerts_sent_today(self) -> int:
        """
        Get the number of alerts sent today.
        
        Returns:
            Number of alerts sent today
        """
        try:
            # TODO: Integrate with alert history service to get actual count
            # For now, return a placeholder
            return 0
            
        except Exception as e:
            logger.error(f"Error getting alerts sent today: {str(e)}")
            return 0
    
    def _is_cooldown_active(self) -> bool:
        """
        Check if alert cooldown is currently active.
        
        Returns:
            True if cooldown is active, False otherwise
        """
        try:
            if not self.preferences:
                return False
            
            # TODO: Integrate with alert history service to check actual cooldown
            # For now, return False
            return False
            
        except Exception as e:
            logger.error(f"Error checking cooldown status: {str(e)}")
            return False
    
    def get_effective_threshold(self, stock_symbol: str = None) -> float:
        """
        Get the effective alert threshold for a stock.
        
        This method checks for individual stock thresholds first, then falls back
        to the global threshold if no individual threshold is set.
        
        Args:
            stock_symbol: Stock symbol to get threshold for
            
        Returns:
            Effective alert threshold percentage
        """
        try:
            if not self.preferences:
                return 3.0  # Default threshold
            
            # If no stock symbol provided, return global threshold
            if not stock_symbol:
                return self.preferences.global_alert_threshold
            
            # Try to get individual stock threshold from stock list service
            try:
                from .stock_list_service import StockListService
                stock_list_service = StockListService()
                
                # Get the stock from the tracked stocks list
                tracked_stocks = stock_list_service.get_all_stocks()
                if tracked_stocks and isinstance(tracked_stocks, list):
                    for stock in tracked_stocks:
                        if stock.symbol.upper() == stock_symbol.upper():
                            logger.info(f"Using individual threshold {stock.alert_threshold}% for {stock_symbol}")
                            return stock.alert_threshold
                
                logger.info(f"No individual threshold found for {stock_symbol}, using global threshold {self.preferences.global_alert_threshold}%")
                
            except Exception as e:
                logger.warning(f"Error getting individual threshold for {stock_symbol}: {str(e)}")
            
            # Fall back to global threshold
            return self.preferences.global_alert_threshold
            
        except Exception as e:
            logger.error(f"Error getting effective threshold: {str(e)}")
            return 1.0
    
    def should_send_alert(self, stock_symbol: str) -> bool:
        """
        Check if an alert should be sent based on preferences.
        
        Args:
            stock_symbol: Stock symbol
            
        Returns:
            True if alert should be sent, False otherwise
        """
        try:
            if not self.preferences or not self.preferences.is_active:
                return False
            
            # Check if email alerts are enabled
            if not self.preferences.email_alerts_enabled:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking if alert should be sent: {str(e)}")
            return False
