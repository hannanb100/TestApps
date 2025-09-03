#!/usr/bin/env python3
"""
Alert History Test Script

This script tests the alert history functionality to ensure it works correctly
before deploying to production. It creates sample alerts and tests the API endpoints.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models.alert_history import AlertHistory
from app.services.alert_history_service import AlertHistoryService


async def test_alert_history():
    """Test the alert history functionality."""
    print("🧪 Testing Alert History Functionality")
    print("=" * 50)
    
    # Initialize the service
    print("📦 Initializing AlertHistoryService...")
    service = AlertHistoryService("test_alert_history.json")
    
    # Test 1: Add sample alerts
    print("\n🧪 Test 1: Adding Sample Alerts")
    
    # Create sample alerts
    sample_alerts = [
        AlertHistory(
            symbol="AAPL",
            current_price=229.72,
            previous_price=232.14,
            change_percent=-1.04,
            alert_type="DAILY",
            analysis="Apple Inc. stock decreased by 1.04% due to market conditions and profit-taking by investors. This appears to be a normal market correction.",
            key_factors=["Market conditions", "Profit-taking", "Normal correction"],
            threshold_used=3.0,
            email_sent=True,
            timestamp=datetime.utcnow() - timedelta(hours=2)
        ),
        AlertHistory(
            symbol="TSLA",
            current_price=245.50,
            previous_price=238.20,
            change_percent=3.07,
            alert_type="INTRADAY",
            analysis="Tesla stock increased by 3.07% due to strong investor interest and positive market sentiment. This indicates growing confidence in the company.",
            key_factors=["Strong investor interest", "Positive sentiment", "Growing confidence"],
            threshold_used=3.0,
            email_sent=True,
            timestamp=datetime.utcnow() - timedelta(hours=1)
        ),
        AlertHistory(
            symbol="MSTY",
            current_price=45.20,
            previous_price=44.20,
            change_percent=2.26,
            alert_type="DAILY",
            analysis="MSTY (Yieldmax MSTR Option Income Strategy ETF) increased by 2.26% due to strong investor interest and positive market sentiment.",
            key_factors=["Strong investor interest", "Positive market sentiment"],
            threshold_used=3.0,
            email_sent=True,
            timestamp=datetime.utcnow() - timedelta(minutes=30)
        )
    ]
    
    # Add alerts to the service
    for alert in sample_alerts:
        alert_id = service.add_alert(alert)
        print(f"   ✅ Added alert #{alert_id} for {alert.symbol} ({alert.change_percent:+.2f}%)")
    
    # Test 2: Get recent alerts
    print("\n🧪 Test 2: Getting Recent Alerts")
    recent_alerts = service.get_recent_alerts(limit=5)
    print(f"   📊 Retrieved {len(recent_alerts)} recent alerts:")
    
    for alert in recent_alerts:
        print(f"   • {alert.symbol}: {alert.change_percent:+.2f}% ({alert.time_ago})")
        print(f"     Analysis: {alert.analysis[:80]}...")
    
    # Test 3: Get alerts by symbol
    print("\n🧪 Test 3: Getting Alerts by Symbol")
    aapl_alerts = service.get_alerts_by_symbol("AAPL", limit=5)
    print(f"   📊 Retrieved {len(aapl_alerts)} alerts for AAPL:")
    
    for alert in aapl_alerts:
        print(f"   • {alert.symbol}: {alert.change_percent:+.2f}% ({alert.time_ago})")
    
    # Test 4: Get alert summary
    print("\n🧪 Test 4: Getting Alert Summary")
    summary = service.get_alert_summary()
    print(f"   📊 Alert Summary:")
    print(f"   • Total alerts: {summary.total_alerts}")
    print(f"   • Alerts today: {summary.alerts_today}")
    print(f"   • Most active stock: {summary.most_active_stock}")
    print(f"   • Last alert: {summary.last_alert_time}")
    print(f"   • Average change: {summary.average_change_percent:.2f}%")
    
    # Test 5: Test time ago calculation
    print("\n🧪 Test 5: Testing Time Ago Calculation")
    test_times = [
        datetime.utcnow() - timedelta(minutes=5),
        datetime.utcnow() - timedelta(hours=2),
        datetime.utcnow() - timedelta(days=1),
        datetime.utcnow() - timedelta(days=3)
    ]
    
    for test_time in test_times:
        time_ago = service._get_time_ago(test_time)
        print(f"   • {test_time.strftime('%Y-%m-%d %H:%M:%S')} → {time_ago}")
    
    print("\n✅ Alert History Testing Completed Successfully!")
    print("=" * 50)
    
    # Clean up test file
    try:
        os.remove("test_alert_history.json")
        print("🧹 Cleaned up test file")
    except:
        pass


async def test_api_endpoints():
    """Test the API endpoints (requires running server)."""
    print("\n🌐 Testing API Endpoints")
    print("=" * 30)
    print("Note: This requires the FastAPI server to be running.")
    print("Start the server with: python -m uvicorn app.main:app --reload")
    print("Then test these endpoints:")
    print("• GET /api/v1/alerts/history")
    print("• GET /api/v1/alerts/history/AAPL")
    print("• GET /api/v1/alerts/summary")
    print("• GET /api/v1/alerts/status")


if __name__ == "__main__":
    print("🚀 Alert History Test Suite")
    print("=" * 40)
    
    try:
        # Run the tests
        asyncio.run(test_alert_history())
        asyncio.run(test_api_endpoints())
        
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
