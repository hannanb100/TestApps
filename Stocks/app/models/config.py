"""
Configuration models for the AI Stock Tracking Agent.

This file handles all the settings and configuration for our app. Think of it as
the "settings panel" where we store all the important information our app needs
to work properly.

What this file does:
- Loads settings from environment variables (like API keys)
- Validates that all required settings are present
- Provides default values for optional settings
- Makes settings available throughout the app

For beginners: Environment variables are a way to store sensitive information
(like API keys) outside of your code. This keeps secrets safe and makes your
app more flexible.
"""

# Standard library imports
from typing import Optional  # For optional values (can be None)
import os  # For operating system interactions

# Third-party imports
from pydantic import Field  # For field validation and documentation
from pydantic_settings import BaseSettings  # For loading settings from environment


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    This class is like a "settings container" that holds all our app's configuration.
    It automatically loads values from environment variables and validates them.
    
    How it works:
    1. Looks for environment variables (like OPENAI_API_KEY)
    2. Validates the data types and formats
    3. Provides default values if variables are missing
    4. Makes all settings available as attributes (like settings.openai_api_key)
    """
    
    # ===== API KEYS SECTION =====
    # These are the "passwords" that let our app talk to external services
    
    openai_api_key: str = Field(
        ...,  # The ... means this is REQUIRED - app won't start without it
        env="OPENAI_API_KEY",  # Look for this environment variable
        description="OpenAI API key for AI analysis - get this from OpenAI.com"
    )
    
    # Twilio settings (for SMS) - these have default "MOCK" values for testing
    twilio_account_sid: str = Field(
        default="MOCK_ACCOUNT_SID",  # Default value if not set
        env="TWILIO_ACCOUNT_SID", 
        description="Twilio Account SID - get this from Twilio.com"
    )
    twilio_auth_token: str = Field(
        default="MOCK_AUTH_TOKEN", 
        env="TWILIO_AUTH_TOKEN", 
        description="Twilio Auth Token - get this from Twilio.com"
    )
    twilio_phone_number: str = Field(
        default="+1555MOCK123", 
        env="TWILIO_PHONE_NUMBER", 
        description="Twilio phone number for sending SMS"
    )
    
    # ===== USER CONFIGURATION SECTION =====
    # Settings that control how the app behaves for the user
    
    user_phone_number: str = Field(
        default="+1555USER123", 
        env="USER_PHONE_NUMBER", 
        description="Your phone number where you want to receive SMS alerts"
    )
    
    # ===== STOCK TRACKING SETTINGS SECTION =====
    # These control how often we check stocks and when to send alerts
    
    alert_threshold_percent: float = Field(
        default=5.0,  # Default: send alert if stock moves 5% or more
        env="ALERT_THRESHOLD_PERCENT", 
        description="Send alert if stock price changes by this percentage (e.g., 5.0 = 5%)"
    )
    check_interval_minutes: int = Field(
        default=60,  # Default: check every 60 minutes (1 hour)
        env="CHECK_INTERVAL_MINUTES", 
        description="How often to check stock prices (in minutes)"
    )
    
    # ===== DATABASE SETTINGS SECTION =====
    # Where we store our data
    
    database_url: str = Field(
        default="sqlite:///./stocks.db",  # Default: SQLite file in current directory
        env="DATABASE_URL", 
        description="Database connection string - SQLite for simple setup"
    )
    
    # ===== APPLICATION SETTINGS SECTION =====
    # General app behavior settings
    
    app_name: str = Field(
        default="AI Stock Tracker", 
        env="APP_NAME",
        description="Name of the application"
    )
    debug: bool = Field(
        default=False, 
        env="DEBUG",
        description="Enable debug mode (shows more detailed error messages)"
    )
    log_level: str = Field(
        default="INFO", 
        env="LOG_LEVEL",
        description="How detailed the logs should be (DEBUG, INFO, WARNING, ERROR)"
    )
    
    # ===== OPTIONAL SETTINGS SECTION =====
    # These are nice-to-have but not required
    
    news_api_key: Optional[str] = Field(
        default=None,  # None means it's optional
        env="NEWS_API_KEY", 
        description="News API key for getting stock-related news (optional)"
    )
    
    # ===== EMAIL CONFIGURATION =====
    # Email settings for sending stock alerts
    # If these are not set, the system will run in mock mode (emails logged to console)
    
    smtp_server: Optional[str] = Field(
        default=None,
        env="SMTP_SERVER",
        description="SMTP server for sending emails (e.g., smtp.gmail.com)"
    )
    
    smtp_port: int = Field(
        default=587,
        env="SMTP_PORT", 
        description="SMTP server port (587 for TLS, 465 for SSL)"
    )
    
    smtp_username: Optional[str] = Field(
        default=None,
        env="SMTP_USERNAME",
        description="SMTP username (usually your email address)"
    )
    
    smtp_password: Optional[str] = Field(
        default=None,
        env="SMTP_PASSWORD", 
        description="SMTP password (use app password for Gmail)"
    )
    
    from_email: Optional[str] = Field(
        default=None,
        env="FROM_EMAIL",
        description="Email address to send alerts from"
    )
    
    to_email: Optional[str] = Field(
        default=None,
        env="TO_EMAIL",
        description="Email address to send alerts to (your email)"
    )
    
    class Config:
        """
        Pydantic configuration class.
        
        This tells Pydantic how to behave when loading settings.
        """
        env_file = "/Users/benhannan/Cursor Apps/APPS/.env"  # Where to find the .env file
        env_file_encoding = "utf-8"  # How to read the file (UTF-8 supports all characters)
        case_sensitive = False  # Don't care about uppercase/lowercase in variable names
        extra = "ignore"  # If there are extra variables in .env, just ignore them


# Create a global instance of our settings
# This makes settings available throughout the app as: settings.openai_api_key
settings = Settings()


class DatabaseConfig:
    """
    Database configuration helper.
    
    Provides database-specific settings and connection management.
    """
    
    @staticmethod
    def get_database_url() -> str:
        """Get the database URL from settings."""
        return settings.database_url
    
    @staticmethod
    def is_sqlite() -> bool:
        """Check if using SQLite database."""
        return settings.database_url.startswith("sqlite")
    
    @staticmethod
    def get_sqlite_path() -> str:
        """Get SQLite database file path."""
        if settings.database_url.startswith("sqlite:///"):
            return settings.database_url.replace("sqlite:///", "")
        return "stocks.db"


class SchedulerConfig:
    """
    Scheduler configuration helper.
    
    Provides settings for the APScheduler cron jobs.
    """
    
    @staticmethod
    def get_check_interval() -> int:
        """Get stock check interval in minutes."""
        return settings.check_interval_minutes
    
    @staticmethod
    def get_alert_threshold() -> float:
        """Get alert threshold percentage."""
        return settings.alert_threshold_percent


class TwilioConfig:
    """
    Twilio configuration helper.
    
    Provides Twilio-specific settings and validation.
    """
    
    @staticmethod
    def get_account_sid() -> str:
        """Get Twilio Account SID."""
        return settings.twilio_account_sid
    
    @staticmethod
    def get_auth_token() -> str:
        """Get Twilio Auth Token."""
        return settings.twilio_auth_token
    
    @staticmethod
    def get_phone_number() -> str:
        """Get Twilio phone number."""
        return settings.twilio_phone_number
    
    @staticmethod
    def get_user_phone() -> str:
        """Get user's phone number."""
        return settings.user_phone_number
