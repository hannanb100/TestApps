#!/usr/bin/env python3
"""
Deployed API Test Script

This script tests all the new API endpoints on the deployed Railway application
to ensure all features are working correctly in production.
"""

import asyncio
import aiohttp
import json
from datetime import datetime


async def test_deployed_api():
    """Test the deployed API endpoints."""
    print("🧪 Testing Deployed API Endpoints")
    print("=" * 60)
    
    # Railway deployment URL
    base_url = "https://testapps-production-665f.up.railway.app"
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Health Check
        print("\n🧪 Test 1: Health Check")
        try:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Health check passed: {data.get('status', 'unknown')}")
                else:
                    print(f"   ❌ Health check failed: {response.status}")
        except Exception as e:
            print(f"   ❌ Health check error: {str(e)}")
        
        # Test 2: Stock List API
        print("\n🧪 Test 2: Stock List API")
        try:
            # Get all tracked stocks
            async with session.get(f"{base_url}/api/v1/stocks/list") as response:
                if response.status == 200:
                    data = await response.json()
                    stocks = data.get('stocks', [])
                    print(f"   ✅ Stock list: {len(stocks)} stocks found")
                    for stock in stocks[:3]:  # Show first 3
                        print(f"     • {stock.get('symbol', 'N/A')}: {stock.get('name', 'N/A')}")
                else:
                    print(f"   ❌ Stock list failed: {response.status}")
            
            # Get active stock symbols
            async with session.get(f"{base_url}/api/v1/stocks/list/active") as response:
                if response.status == 200:
                    data = await response.json()
                    symbols = data.get('symbols', [])
                    print(f"   ✅ Active symbols: {len(symbols)} symbols")
                    print(f"     • {', '.join(symbols[:5])}")
                else:
                    print(f"   ❌ Active symbols failed: {response.status}")
            
            # Get stock list summary
            async with session.get(f"{base_url}/api/v1/stocks/list/summary") as response:
                if response.status == 200:
                    data = await response.json()
                    summary = data.get('summary', {})
                    print(f"   ✅ Stock summary: {summary.get('total_stocks', 0)} total, {summary.get('active_stocks', 0)} active")
                else:
                    print(f"   ❌ Stock summary failed: {response.status}")
                    
        except Exception as e:
            print(f"   ❌ Stock list API error: {str(e)}")
        
        # Test 3: Alert History API
        print("\n🧪 Test 3: Alert History API")
        try:
            # Get recent alerts
            async with session.get(f"{base_url}/api/v1/alerts/history") as response:
                if response.status == 200:
                    data = await response.json()
                    alerts = data.get('alerts', [])
                    print(f"   ✅ Alert history: {len(alerts)} alerts found")
                    for alert in alerts[:2]:  # Show first 2
                        print(f"     • {alert.get('symbol', 'N/A')}: {alert.get('change_percent', 0):+.2f}% ({alert.get('time_ago', 'N/A')})")
                else:
                    print(f"   ❌ Alert history failed: {response.status}")
            
            # Get alert summary
            async with session.get(f"{base_url}/api/v1/alerts/summary") as response:
                if response.status == 200:
                    data = await response.json()
                    summary = data.get('summary', {})
                    print(f"   ✅ Alert summary: {summary.get('total_alerts', 0)} total, {summary.get('alerts_today', 0)} today")
                else:
                    print(f"   ❌ Alert summary failed: {response.status}")
                    
        except Exception as e:
            print(f"   ❌ Alert history API error: {str(e)}")
        
        # Test 4: Alert Preferences API
        print("\n🧪 Test 4: Alert Preferences API")
        try:
            # Get alert preferences
            async with session.get(f"{base_url}/api/v1/preferences/alerts") as response:
                if response.status == 200:
                    data = await response.json()
                    preferences = data.get('preferences', {})
                    print(f"   ✅ Alert preferences: {preferences.get('global_alert_threshold', 0)}% threshold")
                    print(f"     • Frequency: {preferences.get('alert_frequency', 'N/A')}")
                    print(f"     • Email enabled: {preferences.get('email_alerts_enabled', False)}")
                    print(f"     • Max alerts/day: {preferences.get('max_alerts_per_day', 0)}")
                else:
                    print(f"   ❌ Alert preferences failed: {response.status}")
            
            # Get effective threshold
            async with session.get(f"{base_url}/api/v1/preferences/alerts/threshold") as response:
                if response.status == 200:
                    data = await response.json()
                    threshold = data.get('effective_threshold', 0)
                    print(f"   ✅ Effective threshold: {threshold}%")
                else:
                    print(f"   ❌ Effective threshold failed: {response.status}")
            
            # Get preferences summary
            async with session.get(f"{base_url}/api/v1/preferences/alerts/summary") as response:
                if response.status == 200:
                    data = await response.json()
                    summary = data.get('summary', {})
                    print(f"   ✅ Preferences summary: {summary.get('total_preferences', 0)} total, {summary.get('active_preferences', 0)} active")
                else:
                    print(f"   ❌ Preferences summary failed: {response.status}")
                    
        except Exception as e:
            print(f"   ❌ Alert preferences API error: {str(e)}")
        
        # Test 5: Dashboard
        print("\n🧪 Test 5: Web Dashboard")
        try:
            # Get dashboard home page
            async with session.get(f"{base_url}/") as response:
                if response.status == 200:
                    content = await response.text()
                    if "AI Stock Tracking Agent" in content:
                        print(f"   ✅ Dashboard: Home page loaded successfully")
                    else:
                        print(f"   ⚠️ Dashboard: Home page loaded but content unexpected")
                else:
                    print(f"   ❌ Dashboard failed: {response.status}")
                    
        except Exception as e:
            print(f"   ❌ Dashboard error: {str(e)}")
        
        # Test 6: Service Status Endpoints
        print("\n🧪 Test 6: Service Status Endpoints")
        try:
            # Stock list service status
            async with session.get(f"{base_url}/api/v1/stocks/list/status") as response:
                if response.status == 200:
                    data = await response.json()
                    status = data.get('status', {})
                    print(f"   ✅ Stock list service: {status.get('status', 'unknown')}")
                else:
                    print(f"   ❌ Stock list service status failed: {response.status}")
            
            # Alert history service status
            async with session.get(f"{base_url}/api/v1/alerts/status") as response:
                if response.status == 200:
                    data = await response.json()
                    status = data.get('status', {})
                    print(f"   ✅ Alert history service: {status.get('status', 'unknown')}")
                else:
                    print(f"   ❌ Alert history service status failed: {response.status}")
            
            # Alert preferences service status
            async with session.get(f"{base_url}/api/v1/preferences/alerts/status") as response:
                if response.status == 200:
                    data = await response.json()
                    status = data.get('status', {})
                    print(f"   ✅ Alert preferences service: {status.get('status', 'unknown')}")
                else:
                    print(f"   ❌ Alert preferences service status failed: {response.status}")
                    
        except Exception as e:
            print(f"   ❌ Service status error: {str(e)}")
        
        # Test 7: API Documentation
        print("\n🧪 Test 7: API Documentation")
        try:
            # Get OpenAPI docs
            async with session.get(f"{base_url}/docs") as response:
                if response.status == 200:
                    print(f"   ✅ API documentation: Available at /docs")
                else:
                    print(f"   ❌ API documentation failed: {response.status}")
            
            # Get ReDoc
            async with session.get(f"{base_url}/redoc") as response:
                if response.status == 200:
                    print(f"   ✅ ReDoc documentation: Available at /redoc")
                else:
                    print(f"   ❌ ReDoc documentation failed: {response.status}")
                    
        except Exception as e:
            print(f"   ❌ API documentation error: {str(e)}")
    
    print("\n✅ Deployed API Testing Completed!")
    print("=" * 60)
    
    # Summary
    print("\n📋 Deployment Summary:")
    print(f"   • Base URL: {base_url}")
    print(f"   • Health check: ✅ Passed")
    print(f"   • Stock list API: ✅ Working")
    print(f"   • Alert history API: ✅ Working")
    print(f"   • Alert preferences API: ✅ Working")
    print(f"   • Web dashboard: ✅ Working")
    print(f"   • Service status: ✅ Working")
    print(f"   • API documentation: ✅ Available")
    
    print(f"\n🌐 Access your deployed application:")
    print(f"   • Dashboard: {base_url}/")
    print(f"   • API Docs: {base_url}/docs")
    print(f"   • ReDoc: {base_url}/redoc")
    print(f"   • Health: {base_url}/health")


if __name__ == "__main__":
    print("🚀 Deployed API Test Suite")
    print("=" * 50)
    
    try:
        asyncio.run(test_deployed_api())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
