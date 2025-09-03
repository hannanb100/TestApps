#!/usr/bin/env python3
"""
Stock List Initialization Test

This script tests if the stock list service properly initializes
with the default stocks when no database file exists.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.stock_list_service import StockListService


async def test_stock_list_initialization():
    """Test the stock list initialization."""
    print("🧪 Testing Stock List Initialization")
    print("=" * 50)
    
    # Remove any existing tracked_stocks.json file
    test_file = "test_tracked_stocks.json"
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"   🧹 Removed existing {test_file}")
    
    # Initialize the service (should create default stocks)
    print("\n📦 Initializing StockListService with fresh database...")
    service = StockListService(test_file)
    
    # Check if default stocks were created
    print("\n🔍 Checking Default Stocks...")
    all_stocks = service.get_all_stocks()
    active_symbols = service.get_active_stocks()
    summary = service.get_stock_list_summary()
    
    print(f"   📊 Results:")
    print(f"   • Total stocks: {len(all_stocks)}")
    print(f"   • Active symbols: {len(active_symbols)}")
    print(f"   • Summary total: {summary.total_stocks}")
    print(f"   • Summary active: {summary.active_stocks}")
    
    # Show the stocks
    print(f"\n📋 Default Stocks Created:")
    for i, stock in enumerate(all_stocks, 1):
        print(f"   {i:2d}. {stock.symbol:6s} - {stock.name}")
        print(f"       Threshold: {stock.alert_threshold}% | Type: {stock.alert_type}")
    
    # Check if the expected default stocks are present
    expected_stocks = ["VOO", "QQQM", "SCHD", "VT", "SPLG", "SPY", "JEPI", "MSTY", "ARKK", "WDAY"]
    found_stocks = [stock.symbol for stock in all_stocks]
    
    print(f"\n✅ Verification:")
    print(f"   • Expected stocks: {len(expected_stocks)}")
    print(f"   • Found stocks: {len(found_stocks)}")
    
    missing_stocks = set(expected_stocks) - set(found_stocks)
    extra_stocks = set(found_stocks) - set(expected_stocks)
    
    if missing_stocks:
        print(f"   ❌ Missing stocks: {missing_stocks}")
    else:
        print(f"   ✅ All expected stocks present")
    
    if extra_stocks:
        print(f"   ⚠️ Extra stocks: {extra_stocks}")
    
    # Check if file was created
    if os.path.exists(test_file):
        file_size = os.path.getsize(test_file)
        print(f"\n📁 Database file created:")
        print(f"   • File: {test_file}")
        print(f"   • Size: {file_size} bytes")
        
        # Show a snippet of the file
        with open(test_file, 'r') as f:
            content = f.read()
            print(f"   • Content preview: {content[:100]}...")
    else:
        print(f"\n❌ Database file was not created!")
    
    print("\n✅ Stock List Initialization Test Completed!")
    print("=" * 50)
    
    # Clean up
    try:
        os.remove(test_file)
        print("🧹 Cleaned up test file")
    except:
        pass


if __name__ == "__main__":
    print("🚀 Stock List Initialization Test Suite")
    print("=" * 50)
    
    try:
        asyncio.run(test_stock_list_initialization())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
