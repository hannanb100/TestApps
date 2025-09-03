#!/usr/bin/env python3
"""
Dynamic Stock List Test Script

This script tests the dynamic stock list functionality including
adding, removing, updating, and retrieving tracked stocks.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.stock_list_service import StockListService
from app.models.stock_list import AddStockRequest, UpdateStockRequest


async def test_dynamic_stock_list():
    """Test the dynamic stock list functionality."""
    print("🧪 Testing Dynamic Stock List Functionality")
    print("=" * 60)
    
    # Initialize the service
    print("📦 Initializing StockListService...")
    service = StockListService("test_tracked_stocks.json")
    
    # Test 1: Get initial stock list
    print("\n🧪 Test 1: Getting Initial Stock List")
    all_stocks = service.get_all_stocks()
    print(f"   📊 Initial tracked stocks: {len(all_stocks)}")
    
    for stock in all_stocks[:5]:  # Show first 5
        print(f"   • {stock.symbol}: {stock.name} (Threshold: {stock.alert_threshold}%)")
    
    if len(all_stocks) > 5:
        print(f"   ... and {len(all_stocks) - 5} more stocks")
    
    # Test 2: Get active stock symbols
    print("\n🧪 Test 2: Getting Active Stock Symbols")
    active_symbols = service.get_active_stocks()
    print(f"   📊 Active stock symbols: {len(active_symbols)}")
    print(f"   • {', '.join(active_symbols[:10])}")
    if len(active_symbols) > 10:
        print(f"   ... and {len(active_symbols) - 10} more")
    
    # Test 3: Add a new stock
    print("\n🧪 Test 3: Adding New Stock")
    add_request = AddStockRequest(
        symbol="AAPL",
        name="Apple Inc.",
        alert_threshold=2.5,
        alert_type="BOTH",
        notes="Test addition of Apple stock"
    )
    
    new_stock = service.add_stock(add_request)
    if new_stock:
        print(f"   ✅ Added {new_stock.symbol}: {new_stock.name}")
        print(f"   • ID: {new_stock.id}")
        print(f"   • Threshold: {new_stock.alert_threshold}%")
        print(f"   • Type: {new_stock.alert_type}")
        print(f"   • Notes: {new_stock.notes}")
    else:
        print("   ❌ Failed to add stock (may already exist)")
    
    # Test 4: Try to add duplicate stock
    print("\n🧪 Test 4: Adding Duplicate Stock (Should Fail)")
    duplicate_request = AddStockRequest(
        symbol="AAPL",
        name="Apple Inc.",
        alert_threshold=3.0
    )
    
    duplicate_stock = service.add_stock(duplicate_request)
    if duplicate_stock:
        print("   ❌ Unexpectedly added duplicate stock")
    else:
        print("   ✅ Correctly rejected duplicate stock")
    
    # Test 5: Update existing stock
    print("\n🧪 Test 5: Updating Existing Stock")
    if new_stock:
        update_request = UpdateStockRequest(
            alert_threshold=1.5,
            alert_type="DAILY",
            notes="Updated Apple stock settings"
        )
        
        updated_stock = service.update_stock(new_stock.id, update_request)
        if updated_stock:
            print(f"   ✅ Updated {updated_stock.symbol}")
            print(f"   • New threshold: {updated_stock.alert_threshold}%")
            print(f"   • New type: {updated_stock.alert_type}")
            print(f"   • New notes: {updated_stock.notes}")
        else:
            print("   ❌ Failed to update stock")
    
    # Test 6: Get stock by ID
    print("\n🧪 Test 6: Getting Stock by ID")
    if new_stock:
        stock_by_id = service.get_stock_by_id(new_stock.id)
        if stock_by_id:
            print(f"   ✅ Retrieved stock by ID: {stock_by_id.symbol}")
            print(f"   • Name: {stock_by_id.name}")
            print(f"   • Days tracked: {stock_by_id.days_tracked}")
            print(f"   • Current price: ${stock_by_id.current_price or 'N/A'}")
        else:
            print("   ❌ Failed to retrieve stock by ID")
    
    # Test 7: Get stock list summary
    print("\n🧪 Test 7: Getting Stock List Summary")
    summary = service.get_stock_list_summary()
    print(f"   📊 Stock List Summary:")
    print(f"   • Total stocks: {summary.total_stocks}")
    print(f"   • Active stocks: {summary.active_stocks}")
    print(f"   • Inactive stocks: {summary.inactive_stocks}")
    print(f"   • Average threshold: {summary.average_threshold:.2f}%")
    print(f"   • Most recent addition: {summary.most_recent_addition}")
    
    # Test 8: Add another stock for testing
    print("\n🧪 Test 8: Adding Another Stock")
    add_request2 = AddStockRequest(
        symbol="TSLA",
        name="Tesla Inc.",
        alert_threshold=4.0,
        alert_type="INTRADAY",
        notes="Tesla for intraday monitoring"
    )
    
    new_stock2 = service.add_stock(add_request2)
    if new_stock2:
        print(f"   ✅ Added {new_stock2.symbol}: {new_stock2.name}")
    else:
        print("   ❌ Failed to add Tesla stock")
    
    # Test 9: Remove a stock
    print("\n🧪 Test 9: Removing a Stock")
    if new_stock2:
        success = service.remove_stock(new_stock2.id)
        if success:
            print(f"   ✅ Removed {new_stock2.symbol} from tracking")
        else:
            print(f"   ❌ Failed to remove {new_stock2.symbol}")
    
    # Test 10: Final summary
    print("\n🧪 Test 10: Final Summary")
    final_stocks = service.get_all_stocks()
    final_active = service.get_active_stocks()
    final_summary = service.get_stock_list_summary()
    
    print(f"   📊 Final Results:")
    print(f"   • Total tracked stocks: {len(final_stocks)}")
    print(f"   • Active stock symbols: {len(final_active)}")
    print(f"   • Summary total: {final_summary.total_stocks}")
    print(f"   • Summary active: {final_summary.active_stocks}")
    
    print("\n✅ Dynamic Stock List Testing Completed Successfully!")
    print("=" * 60)
    
    # Show available API endpoints
    print("\n🌐 Available API Endpoints:")
    print("   • GET /api/v1/stocks/list - Get all tracked stocks")
    print("   • GET /api/v1/stocks/list/active - Get active stock symbols")
    print("   • GET /api/v1/stocks/list/{id} - Get specific tracked stock")
    print("   • POST /api/v1/stocks/list - Add new tracked stock")
    print("   • PUT /api/v1/stocks/list/{id} - Update tracked stock")
    print("   • DELETE /api/v1/stocks/list/{id} - Remove tracked stock")
    print("   • GET /api/v1/stocks/list/summary - Get stock list summary")
    print("   • GET /api/v1/stocks/list/status - Get service status")
    
    # Clean up test file
    try:
        os.remove("test_tracked_stocks.json")
        print("\n🧹 Cleaned up test file")
    except:
        pass


if __name__ == "__main__":
    print("🚀 Dynamic Stock List Test Suite")
    print("=" * 50)
    
    try:
        asyncio.run(test_dynamic_stock_list())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
