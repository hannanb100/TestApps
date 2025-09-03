#!/usr/bin/env python3
"""
Initialize Railway Database Files

This script creates the necessary database files for the Railway deployment
with default data so the API endpoints work correctly.
"""

import json
import os
from datetime import datetime

def create_tracked_stocks_file():
    """Create the tracked_stocks.json file with default stocks."""
    default_stocks = [
        {
            "id": 1,
            "symbol": "VOO",
            "name": "Vanguard S&P 500 ETF",
            "alert_threshold": 3.0,
            "alert_type": "DAILY",
            "is_active": True,
            "added_date": datetime.utcnow().isoformat(),
            "current_price": None
        },
        {
            "id": 2,
            "symbol": "QQQM",
            "name": "Invesco NASDAQ 100 ETF",
            "alert_threshold": 3.0,
            "alert_type": "DAILY",
            "is_active": True,
            "added_date": datetime.utcnow().isoformat(),
            "current_price": None
        },
        {
            "id": 3,
            "symbol": "SCHD",
            "name": "Schwab U.S. Dividend Equity ETF",
            "alert_threshold": 3.0,
            "alert_type": "DAILY",
            "is_active": True,
            "added_date": datetime.utcnow().isoformat(),
            "current_price": None
        },
        {
            "id": 4,
            "symbol": "VT",
            "name": "Vanguard Total World Stock ETF",
            "alert_threshold": 3.0,
            "alert_type": "DAILY",
            "is_active": True,
            "added_date": datetime.utcnow().isoformat(),
            "current_price": None
        },
        {
            "id": 5,
            "symbol": "SPLG",
            "name": "SPDR Portfolio S&P 500 ETF",
            "alert_threshold": 3.0,
            "alert_type": "DAILY",
            "is_active": True,
            "added_date": datetime.utcnow().isoformat(),
            "current_price": None
        },
        {
            "id": 6,
            "symbol": "SPY",
            "name": "SPDR S&P 500 ETF Trust",
            "alert_threshold": 3.0,
            "alert_type": "DAILY",
            "is_active": True,
            "added_date": datetime.utcnow().isoformat(),
            "current_price": None
        },
        {
            "id": 7,
            "symbol": "JEPI",
            "name": "JPMorgan Equity Premium Income ETF",
            "alert_threshold": 3.0,
            "alert_type": "DAILY",
            "is_active": True,
            "added_date": datetime.utcnow().isoformat(),
            "current_price": None
        },
        {
            "id": 8,
            "symbol": "MSTY",
            "name": "YieldMax TSLA Option Income Strategy ETF",
            "alert_threshold": 3.0,
            "alert_type": "DAILY",
            "is_active": True,
            "added_date": datetime.utcnow().isoformat(),
            "current_price": None
        },
        {
            "id": 9,
            "symbol": "ARKK",
            "name": "ARK Innovation ETF",
            "alert_threshold": 3.0,
            "alert_type": "DAILY",
            "is_active": True,
            "added_date": datetime.utcnow().isoformat(),
            "current_price": None
        },
        {
            "id": 10,
            "symbol": "WDAY",
            "name": "Workday Inc.",
            "alert_threshold": 3.0,
            "alert_type": "DAILY",
            "is_active": True,
            "added_date": datetime.utcnow().isoformat(),
            "current_price": None
        }
    ]
    
    with open("tracked_stocks.json", "w") as f:
        json.dump(default_stocks, f, indent=2)
    
    print(f"✅ Created tracked_stocks.json with {len(default_stocks)} stocks")

def create_alert_preferences_file():
    """Create the alert_preferences.json file with default preferences."""
    default_preferences = {
        "id": 1,
        "global_alert_threshold": 3.0,
        "alert_frequency": "MARKET_HOURS",
        "market_hours_only": True,
        "alert_types": ["DAILY", "INTRADAY"],
        "email_alerts_enabled": True,
        "email_rich_format": True,
        "sms_alerts_enabled": False,
        "include_analysis": True,
        "include_key_factors": True,
        "include_price_history": False,
        "max_alerts_per_day": 10,
        "alert_cooldown_minutes": 30,
        "enable_volume_alerts": False,
        "volume_threshold_multiplier": 2.0,
        "enable_news_alerts": True,
        "news_sentiment_threshold": 0.7,
        "custom_schedule": None,
        "created_date": datetime.utcnow().isoformat(),
        "updated_date": datetime.utcnow().isoformat(),
        "is_active": True
    }
    
    with open("alert_preferences.json", "w") as f:
        json.dump(default_preferences, f, indent=2)
    
    print("✅ Created alert_preferences.json with default settings")

def create_alert_history_file():
    """Create the alert_history.json file (empty initially)."""
    empty_history = []
    
    with open("alert_history.json", "w") as f:
        json.dump(empty_history, f, indent=2)
    
    print("✅ Created alert_history.json (empty)")

def main():
    """Initialize all database files."""
    print("🚀 Initializing Railway Database Files")
    print("=" * 50)
    
    # Create all database files
    create_tracked_stocks_file()
    create_alert_preferences_file()
    create_alert_history_file()
    
    print("\n✅ All database files created successfully!")
    print("=" * 50)
    
    # Show file sizes
    files = ["tracked_stocks.json", "alert_preferences.json", "alert_history.json"]
    total_size = 0
    
    for file in files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            total_size += size
            print(f"📄 {file}: {size:,} bytes")
    
    print(f"📊 Total database size: {total_size:,} bytes")
    
    print("\n🌐 Your Railway app should now work correctly!")
    print("   • Stock list API: ✅ Ready")
    print("   • Alert preferences API: ✅ Ready")
    print("   • Alert history API: ✅ Ready")

if __name__ == "__main__":
    main()
