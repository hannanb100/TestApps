#!/usr/bin/env python3
"""
Simple test to check if WDAY should trigger an alert
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.stock_service import StockService
from app.services.alert_preferences_service import AlertPreferencesService

async def test_wday_alert():
    print("=== Testing WDAY Alert Logic ===")
    
    # Initialize services
    stock_service = StockService()
    preferences_service = AlertPreferencesService()
    
    # Get WDAY quote
    print("1. Getting WDAY quote...")
    quote = await stock_service.get_stock_quote("WDAY")
    print(f"   Price: ${quote.price}")
    print(f"   Change: {quote.change_percent:+.2f}%")
    
    # Get threshold
    print("2. Getting threshold...")
    threshold = preferences_service.get_effective_threshold("WDAY")
    print(f"   Threshold: {threshold}%")
    
    # Check if should alert
    print("3. Checking if should alert...")
    should_alert = abs(quote.change_percent) >= threshold
    print(f"   Should alert: {should_alert}")
    print(f"   |{quote.change_percent:.2f}| >= {threshold} = {abs(quote.change_percent) >= threshold}")
    
    # Check preferences
    print("4. Checking alert preferences...")
    prefs = preferences_service.get_preferences()
    print(f"   Email alerts enabled: {prefs.email_alerts_enabled}")
    print(f"   Is active: {prefs.is_active}")
    print(f"   Alert types: {prefs.alert_types}")
    
    # Check should_send_alert
    print("5. Checking should_send_alert...")
    should_send = preferences_service.should_send_alert("WDAY", "INTRADAY")
    print(f"   Should send alert: {should_send}")
    
    return should_alert and should_send

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(test_wday_alert())
    print(f"\n=== RESULT: {'SHOULD ALERT' if result else 'NO ALERT'} ===")
