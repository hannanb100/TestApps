#!/usr/bin/env python3
"""
Debug threshold issue
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.alert_preferences_service import AlertPreferencesService
from app.services.stock_list_service import StockListService

def debug_threshold():
    print("=== Debugging Threshold Issue ===")
    
    # Initialize services
    preferences_service = AlertPreferencesService()
    stock_list_service = StockListService()
    
    print("1. Getting WDAY threshold...")
    threshold = preferences_service.get_effective_threshold("WDAY")
    print(f"   Effective threshold: {threshold}%")
    
    print("2. Getting all stocks...")
    all_stocks = stock_list_service.get_all_stocks()
    print(f"   Total stocks: {len(all_stocks)}")
    
    print("3. Looking for WDAY in stocks...")
    wday_found = False
    for stock in all_stocks:
        if stock.symbol.upper() == "WDAY":
            print(f"   Found WDAY: threshold={stock.alert_threshold}%")
            wday_found = True
            break
    
    if not wday_found:
        print("   WDAY not found in stocks list!")
    
    print("4. Getting preferences...")
    preferences = preferences_service.get_preferences()
    if preferences:
        print(f"   Global threshold: {preferences.global_alert_threshold}%")
    else:
        print("   No preferences found!")

if __name__ == "__main__":
    debug_threshold()
