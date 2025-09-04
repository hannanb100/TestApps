"""
Alert History Service - Manages storage and retrieval of alert history.

This service handles storing alert information when alerts are sent,
and provides methods to retrieve alert history for the user interface.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import os

from ..models.alert_history import AlertHistory, AlertHistoryResponse, AlertHistorySummary

# Configure logging
logger = logging.getLogger(__name__)


class AlertHistoryService:
    """
    Service for managing alert history storage and retrieval.
    
    This service stores alert information in a simple JSON file
    for now, but could be easily upgraded to use a database later.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AlertHistoryService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, storage_file: str = "alert_history.json"):
        if self._initialized:
            return
        """
        Initialize the alert history service.
        
        Args:
            storage_file: Path to the JSON file for storing alert history
        """
        self.storage_file = storage_file
        self.alerts: List[AlertHistory] = []
        self._load_alerts()
        logger.info(f"AlertHistoryService initialized with {len(self.alerts)} existing alerts")
        self._initialized = True
    
    def _load_alerts(self):
        """Load existing alerts from the storage file."""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.alerts = [AlertHistory(**alert) for alert in data]
                logger.info(f"Loaded {len(self.alerts)} alerts from {self.storage_file}")
            else:
                self.alerts = []
                logger.info(f"No existing alert history file found at {self.storage_file}")
        except Exception as e:
            logger.error(f"Error loading alert history: {str(e)}")
            self.alerts = []
    
    def _save_alerts(self):
        """Save alerts to the storage file."""
        try:
            # Convert alerts to dictionaries for JSON serialization
            alerts_data = [alert.dict() for alert in self.alerts]
            
            with open(self.storage_file, 'w') as f:
                json.dump(alerts_data, f, indent=2, default=str)
            
            logger.info(f"Saved {len(self.alerts)} alerts to {self.storage_file}")
        except Exception as e:
            logger.error(f"Error saving alert history: {str(e)}")
    
    def add_alert(self, alert: AlertHistory) -> int:
        """
        Add a new alert to the history.
        
        Args:
            alert: The alert to add to history
            
        Returns:
            The ID of the added alert
        """
        try:
            # Assign a unique ID (simple increment for now)
            if self.alerts:
                alert.id = max(alert.id for alert in self.alerts if alert.id) + 1
            else:
                alert.id = 1
            
            # Add to the list
            self.alerts.append(alert)
            
            # Save to file
            self._save_alerts()
            
            logger.info(f"Added alert #{alert.id} for {alert.symbol} ({alert.change_percent:+.2f}%)")
            return alert.id
            
        except Exception as e:
            logger.error(f"Error adding alert to history: {str(e)}")
            return -1
    
    def get_recent_alerts(self, limit: int = 10) -> List[AlertHistoryResponse]:
        """
        Get the most recent alerts.
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of recent alerts with computed fields
        """
        try:
            # Sort by timestamp (newest first) and limit results
            recent_alerts = sorted(self.alerts, key=lambda x: x.timestamp, reverse=True)[:limit]
            
            # Convert to response format with computed fields
            response_alerts = []
            for alert in recent_alerts:
                response_alert = AlertHistoryResponse(
                    id=alert.id,
                    symbol=alert.symbol,
                    current_price=alert.current_price,
                    previous_price=alert.previous_price,
                    change_percent=alert.change_percent,
                    alert_type=alert.alert_type,
                    analysis=alert.analysis,
                    key_factors=alert.key_factors,
                    timestamp=alert.timestamp,
                    threshold_used=alert.threshold_used,
                    email_sent=alert.email_sent,
                    price_change_dollar=alert.current_price - alert.previous_price,
                    time_ago=self._get_time_ago(alert.timestamp)
                )
                response_alerts.append(response_alert)
            
            logger.info(f"Retrieved {len(response_alerts)} recent alerts")
            return response_alerts
            
        except Exception as e:
            logger.error(f"Error getting recent alerts: {str(e)}")
            return []
    
    def get_alerts_by_symbol(self, symbol: str, limit: int = 10) -> List[AlertHistoryResponse]:
        """
        Get alerts for a specific stock symbol.
        
        Args:
            symbol: Stock symbol to filter by
            limit: Maximum number of alerts to return
            
        Returns:
            List of alerts for the specified symbol
        """
        try:
            # Filter by symbol and sort by timestamp
            symbol_alerts = [
                alert for alert in self.alerts 
                if alert.symbol.upper() == symbol.upper()
            ]
            symbol_alerts = sorted(symbol_alerts, key=lambda x: x.timestamp, reverse=True)[:limit]
            
            # Convert to response format
            response_alerts = []
            for alert in symbol_alerts:
                response_alert = AlertHistoryResponse(
                    id=alert.id,
                    symbol=alert.symbol,
                    current_price=alert.current_price,
                    previous_price=alert.previous_price,
                    change_percent=alert.change_percent,
                    alert_type=alert.alert_type,
                    analysis=alert.analysis,
                    key_factors=alert.key_factors,
                    timestamp=alert.timestamp,
                    threshold_used=alert.threshold_used,
                    email_sent=alert.email_sent,
                    price_change_dollar=alert.current_price - alert.previous_price,
                    time_ago=self._get_time_ago(alert.timestamp)
                )
                response_alerts.append(response_alert)
            
            logger.info(f"Retrieved {len(response_alerts)} alerts for {symbol}")
            return response_alerts
            
        except Exception as e:
            logger.error(f"Error getting alerts for {symbol}: {str(e)}")
            return []
    
    def get_alert_summary(self) -> AlertHistorySummary:
        """
        Get a summary of alert activity.
        
        Returns:
            Summary statistics about alert history
        """
        try:
            if not self.alerts:
                return AlertHistorySummary(
                    total_alerts=0,
                    alerts_today=0,
                    most_active_stock="N/A",
                    last_alert_time=None,
                    average_change_percent=0.0
                )
            
            # Calculate statistics
            total_alerts = len(self.alerts)
            
            # Count alerts today
            today = datetime.utcnow().date()
            alerts_today = len([
                alert for alert in self.alerts 
                if alert.timestamp.date() == today
            ])
            
            # Find most active stock
            symbol_counts = {}
            for alert in self.alerts:
                symbol_counts[alert.symbol] = symbol_counts.get(alert.symbol, 0) + 1
            most_active_stock = max(symbol_counts, key=symbol_counts.get) if symbol_counts else "N/A"
            
            # Get last alert time
            last_alert_time = max(alert.timestamp for alert in self.alerts)
            
            # Calculate average change percentage
            average_change_percent = sum(abs(alert.change_percent) for alert in self.alerts) / total_alerts
            
            summary = AlertHistorySummary(
                total_alerts=total_alerts,
                alerts_today=alerts_today,
                most_active_stock=most_active_stock,
                last_alert_time=last_alert_time,
                average_change_percent=average_change_percent
            )
            
            logger.info(f"Generated alert summary: {total_alerts} total alerts, {alerts_today} today")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating alert summary: {str(e)}")
            return AlertHistorySummary(
                total_alerts=0,
                alerts_today=0,
                most_active_stock="N/A",
                last_alert_time=None,
                average_change_percent=0.0
            )
    
    def _get_time_ago(self, timestamp: datetime) -> str:
        """
        Get a human-readable time ago string.
        
        Args:
            timestamp: The timestamp to compare to now
            
        Returns:
            Human-readable time ago string
        """
        try:
            now = datetime.utcnow()
            diff = now - timestamp
            
            if diff.days > 0:
                return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            else:
                return "Just now"
                
        except Exception as e:
            logger.error(f"Error calculating time ago: {str(e)}")
            return "Unknown"
    
    def clear_history(self) -> bool:
        """
        Clear all alert history.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.alerts = []
            self._save_alerts()
            logger.info("Alert history cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing alert history: {str(e)}")
            return False
