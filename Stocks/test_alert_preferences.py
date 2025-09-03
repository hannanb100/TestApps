#!/usr/bin/env python3
"""
Alert Preferences Test Script

This script tests the alert preferences functionality including
creating, updating, and retrieving alert preferences.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.alert_preferences_service import AlertPreferencesService
from app.models.alert_preferences import UpdateAlertPreferencesRequest


async def test_alert_preferences():
    """Test the alert preferences functionality."""
    print("🧪 Testing Alert Preferences Functionality")
    print("=" * 60)
    
    # Initialize the service
    print("📦 Initializing AlertPreferencesService...")
    service = AlertPreferencesService("test_alert_preferences.json")
    
    # Test 1: Get initial preferences
    print("\n🧪 Test 1: Getting Initial Preferences")
    preferences = service.get_preferences()
    if preferences:
        print(f"   📊 Initial Preferences:")
        print(f"   • Global threshold: {preferences.global_alert_threshold}%")
        print(f"   • Alert frequency: {preferences.alert_frequency}")
        print(f"   • Market hours only: {preferences.market_hours_only}")
        print(f"   • Alert types: {preferences.alert_types}")
        print(f"   • Email enabled: {preferences.email_alerts_enabled}")
        print(f"   • Max alerts per day: {preferences.max_alerts_per_day}")
        print(f"   • Cooldown minutes: {preferences.alert_cooldown_minutes}")
        print(f"   • Include analysis: {preferences.include_analysis}")
        print(f"   • Include key factors: {preferences.include_key_factors}")
    else:
        print("   ❌ No preferences found")
    
    # Test 2: Update preferences
    print("\n🧪 Test 2: Updating Preferences")
    update_request = UpdateAlertPreferencesRequest(
        global_alert_threshold=2.5,
        alert_frequency="HOURLY",
        market_hours_only=False,
        max_alerts_per_day=15,
        alert_cooldown_minutes=45,
        include_analysis=True,
        include_key_factors=True
    )
    
    updated_preferences = service.update_preferences(update_request)
    if updated_preferences:
        print(f"   ✅ Updated Preferences:")
        print(f"   • Global threshold: {updated_preferences.global_alert_threshold}%")
        print(f"   • Alert frequency: {updated_preferences.alert_frequency}")
        print(f"   • Market hours only: {updated_preferences.market_hours_only}")
        print(f"   • Max alerts per day: {updated_preferences.max_alerts_per_day}")
        print(f"   • Cooldown minutes: {updated_preferences.alert_cooldown_minutes}")
        print(f"   • Include analysis: {updated_preferences.include_analysis}")
        print(f"   • Include key factors: {updated_preferences.include_key_factors}")
    else:
        print("   ❌ Failed to update preferences")
    
    # Test 3: Get effective threshold
    print("\n🧪 Test 3: Getting Effective Threshold")
    threshold = service.get_effective_threshold("AAPL")
    print(f"   📊 Effective threshold for AAPL: {threshold}%")
    
    threshold_global = service.get_effective_threshold()
    print(f"   📊 Global effective threshold: {threshold_global}%")
    
    # Test 4: Check alert eligibility
    print("\n🧪 Test 4: Checking Alert Eligibility")
    should_send_daily = service.should_send_alert("AAPL", "DAILY")
    should_send_intraday = service.should_send_alert("AAPL", "INTRADAY")
    should_send_weekly = service.should_send_alert("AAPL", "WEEKLY")
    
    print(f"   📊 Alert Eligibility for AAPL:")
    print(f"   • DAILY alert: {'✅ Should send' if should_send_daily else '❌ Should not send'}")
    print(f"   • INTRADAY alert: {'✅ Should send' if should_send_intraday else '❌ Should not send'}")
    print(f"   • WEEKLY alert: {'✅ Should send' if should_send_weekly else '❌ Should not send'}")
    
    # Test 5: Get preferences summary
    print("\n🧪 Test 5: Getting Preferences Summary")
    summary = service.get_preferences_summary()
    print(f"   📊 Preferences Summary:")
    print(f"   • Total preferences: {summary.total_preferences}")
    print(f"   • Active preferences: {summary.active_preferences}")
    print(f"   • Average threshold: {summary.average_threshold}%")
    print(f"   • Most common frequency: {summary.most_common_frequency}")
    print(f"   • Email enabled count: {summary.email_enabled_count}")
    print(f"   • SMS enabled count: {summary.sms_enabled_count}")
    print(f"   • Last updated: {summary.last_updated}")
    
    # Test 6: Reset to defaults
    print("\n🧪 Test 6: Resetting to Defaults")
    reset_preferences = service.reset_to_defaults()
    if reset_preferences:
        print(f"   ✅ Reset to Defaults:")
        print(f"   • Global threshold: {reset_preferences.global_alert_threshold}%")
        print(f"   • Alert frequency: {reset_preferences.alert_frequency}")
        print(f"   • Market hours only: {reset_preferences.market_hours_only}")
        print(f"   • Max alerts per day: {reset_preferences.max_alerts_per_day}")
        print(f"   • Cooldown minutes: {reset_preferences.alert_cooldown_minutes}")
    else:
        print("   ❌ Failed to reset to defaults")
    
    # Test 7: Test computed fields
    print("\n🧪 Test 7: Testing Computed Fields")
    final_preferences = service.get_preferences()
    if final_preferences:
        print(f"   📊 Computed Fields:")
        print(f"   • Next alert time: {final_preferences.next_alert_time}")
        print(f"   • Alerts sent today: {final_preferences.alerts_sent_today}")
        print(f"   • Cooldown active: {final_preferences.cooldown_active}")
        print(f"   • Created date: {final_preferences.created_date}")
        print(f"   • Updated date: {final_preferences.updated_date}")
    
    print("\n✅ Alert Preferences Testing Completed Successfully!")
    print("=" * 60)
    
    # Show available API endpoints
    print("\n🌐 Available API Endpoints:")
    print("   • GET /api/v1/preferences/alerts - Get alert preferences")
    print("   • PUT /api/v1/preferences/alerts - Update alert preferences")
    print("   • POST /api/v1/preferences/alerts/reset - Reset to defaults")
    print("   • GET /api/v1/preferences/alerts/summary - Get preferences summary")
    print("   • GET /api/v1/preferences/alerts/threshold - Get effective threshold")
    print("   • POST /api/v1/preferences/alerts/check - Check alert eligibility")
    print("   • GET /api/v1/preferences/alerts/status - Get service status")
    
    # Clean up test file
    try:
        os.remove("test_alert_preferences.json")
        print("\n🧹 Cleaned up test file")
    except:
        pass


if __name__ == "__main__":
    print("🚀 Alert Preferences Test Suite")
    print("=" * 50)
    
    try:
        asyncio.run(test_alert_preferences())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
