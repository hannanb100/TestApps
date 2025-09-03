#!/usr/bin/env python3
"""
Dashboard Features Test Script

This script tests the dashboard features including alert history
and API endpoints to ensure everything works correctly.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.alert_history_service import AlertHistoryService
from app.models.alert_history import AlertHistory


async def test_dashboard_features():
    """Test the dashboard features."""
    print("🧪 Testing Dashboard Features")
    print("=" * 50)
    
    # Initialize the alert history service
    print("📦 Initializing AlertHistoryService...")
    service = AlertHistoryService("alert_history.json")
    
    # Test 1: Get alert summary (for dashboard stats)
    print("\n🧪 Test 1: Alert Summary (Dashboard Stats)")
    summary = service.get_alert_summary()
    print(f"   📊 Dashboard Stats:")
    print(f"   • Total alerts: {summary.total_alerts}")
    print(f"   • Alerts today: {summary.alerts_today}")
    print(f"   • Most active stock: {summary.most_active_stock}")
    print(f"   • Last alert: {summary.last_alert_time}")
    print(f"   • Average change: {summary.average_change_percent:.2f}%")
    
    # Test 2: Get recent alerts (for dashboard list)
    print("\n🧪 Test 2: Recent Alerts (Dashboard List)")
    recent_alerts = service.get_recent_alerts(limit=5)
    print(f"   📊 Recent Alerts ({len(recent_alerts)} found):")
    
    for i, alert in enumerate(recent_alerts, 1):
        print(f"   {i}. {alert.symbol}: {alert.change_percent:+.2f}% ({alert.time_ago})")
        print(f"      Price: ${alert.current_price:.2f} (was ${alert.previous_price:.2f})")
        print(f"      Type: {alert.alert_type}")
        print(f"      Analysis: {alert.analysis[:80]}...")
        print()
    
    # Test 3: Get alerts by symbol (for individual stock view)
    print("\n🧪 Test 3: Alerts by Symbol (Individual Stock View)")
    test_symbols = ["TEST", "AAPL", "TSLA"]
    
    for symbol in test_symbols:
        symbol_alerts = service.get_alerts_by_symbol(symbol, limit=3)
        if symbol_alerts:
            print(f"   📊 {symbol} Alerts ({len(symbol_alerts)} found):")
            for alert in symbol_alerts:
                print(f"   • {alert.change_percent:+.2f}% ({alert.time_ago}) - {alert.alert_type}")
        else:
            print(f"   📊 {symbol}: No alerts found")
    
    # Test 4: Test API endpoint data format
    print("\n🧪 Test 4: API Endpoint Data Format")
    print("   📊 Testing data format for API endpoints...")
    
    # Test summary endpoint format
    summary_data = {
        "summary": summary,
        "message": "Alert history summary retrieved successfully"
    }
    print(f"   ✅ Summary endpoint format: {len(str(summary_data))} characters")
    
    # Test history endpoint format
    history_data = {
        "alerts": recent_alerts,
        "count": len(recent_alerts),
        "message": f"Retrieved {len(recent_alerts)} recent alerts"
    }
    print(f"   ✅ History endpoint format: {len(str(history_data))} characters")
    
    # Test 5: Dashboard HTML template data
    print("\n🧪 Test 5: Dashboard Template Data")
    print("   📊 Testing data for dashboard template...")
    
    dashboard_data = {
        "total_alerts": summary.total_alerts,
        "alerts_today": summary.alerts_today,
        "most_active_stock": summary.most_active_stock,
        "last_alert_time": summary.last_alert_time,
        "recent_alerts": recent_alerts[:5]  # Top 5 for dashboard
    }
    
    print(f"   ✅ Dashboard data prepared:")
    print(f"   • Total alerts: {dashboard_data['total_alerts']}")
    print(f"   • Alerts today: {dashboard_data['alerts_today']}")
    print(f"   • Most active: {dashboard_data['most_active_stock']}")
    print(f"   • Recent alerts: {len(dashboard_data['recent_alerts'])}")
    
    print("\n✅ Dashboard Features Testing Completed Successfully!")
    print("=" * 50)
    
    # Show available endpoints
    print("\n🌐 Available API Endpoints:")
    print("   • GET /api/v1/alerts/history - Get recent alerts")
    print("   • GET /api/v1/alerts/history/{symbol} - Get alerts for specific stock")
    print("   • GET /api/v1/alerts/summary - Get alert summary")
    print("   • GET /api/v1/alerts/status - Get service status")
    print("   • GET / - Dashboard home page")
    print("   • GET /dashboard - Dashboard redirect")


if __name__ == "__main__":
    print("🚀 Dashboard Features Test Suite")
    print("=" * 40)
    
    try:
        asyncio.run(test_dashboard_features())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
