#!/usr/bin/env python3
"""
Integration Test Script

This script tests the integration of alert history with the email service
to ensure alerts are properly logged when emails are sent.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.email_service import EmailService
from app.services.alert_history_service import AlertHistoryService


async def test_alert_integration():
    """Test the integration between email service and alert history."""
    print("🧪 Testing Alert History Integration")
    print("=" * 50)
    
    # Initialize services
    print("📦 Initializing services...")
    email_service = EmailService()
    alert_service = AlertHistoryService("alert_history.json")
    
    # Test sending a stock alert (this should log to history)
    print("\n🧪 Test: Sending Stock Alert with History Logging")
    
    try:
        # Send a test alert
        email_result = await email_service.send_stock_alert(
            symbol="TEST",
            current_price=150.25,
            previous_price=145.00,
            change_percent=3.62,
            analysis="Test stock increased by 3.62% due to strong investor interest and positive market sentiment. This is a test alert to verify the integration between email service and alert history.",
            key_factors=["Test integration", "Strong investor interest", "Positive sentiment"],
            alert_type="INTRADAY"
        )
        
        if email_result:
            print("   ✅ Email sent successfully")
        else:
            print("   ⚠️ Email not sent (likely in mock mode)")
        
        # Check if alert was logged to history
        print("\n🔍 Checking Alert History...")
        recent_alerts = alert_service.get_recent_alerts(limit=5)
        
        if recent_alerts:
            print(f"   📊 Found {len(recent_alerts)} alerts in history:")
            for alert in recent_alerts:
                print(f"   • {alert.symbol}: {alert.change_percent:+.2f}% ({alert.time_ago})")
                print(f"     Analysis: {alert.analysis[:60]}...")
        else:
            print("   ❌ No alerts found in history")
        
        # Test alert summary
        print("\n📊 Alert Summary:")
        summary = alert_service.get_alert_summary()
        print(f"   • Total alerts: {summary.total_alerts}")
        print(f"   • Alerts today: {summary.alerts_today}")
        print(f"   • Most active stock: {summary.most_active_stock}")
        print(f"   • Last alert: {summary.last_alert_time}")
        
    except Exception as e:
        print(f"   ❌ Error during integration test: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Note: We're using the main alert_history.json file, so no cleanup needed
    print("\n📝 Note: Alerts are stored in alert_history.json")
    
    print("\n✅ Integration Test Completed!")
    print("=" * 50)


if __name__ == "__main__":
    print("🚀 Alert History Integration Test")
    print("=" * 40)
    
    try:
        asyncio.run(test_alert_integration())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
