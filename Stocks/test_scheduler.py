#!/usr/bin/env python3
"""
Scheduler Testing Script - Test the background stock monitoring.

This script tests the background scheduler that automatically checks
stock prices and sends alerts when thresholds are exceeded.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.mock_sms_service import MockSMSService
from app.services.stock_service import StockService
from app.services.agent_service import AgentService
from app.services.scheduler_service import SchedulerService
from app.models.config import settings


async def test_scheduler():
    """
    Test the background scheduler with stock monitoring.
    
    This function starts the scheduler and simulates it running
    for a few cycles to test the automated monitoring system.
    """
    print("🚀 Scheduler Testing")
    print("=" * 40)
    
    # Initialize services
    print("🔄 Initializing services...")
    stock_service = StockService()
    sms_service = MockSMSService()
    agent_service = AgentService()
    scheduler_service = SchedulerService()
    
    # Test stocks to monitor
    test_stocks = ["AAPL", "TSLA", "GOOGL", "MSFT"]
    print(f"📋 Monitoring stocks: {', '.join(test_stocks)}")
    print(f"🎯 Alert threshold: {settings.alert_threshold_percent}%")
    print(f"⏰ Check interval: {settings.check_interval_minutes} minutes")
    
    try:
        # Start the scheduler
        print("\n🔄 Starting scheduler...")
        await scheduler_service.start()
        
        print("✅ Scheduler started successfully!")
        print("📊 The scheduler will now check stock prices automatically...")
        print("💡 In a real scenario, this would run continuously in the background")
        
        # Simulate running for a few cycles
        print(f"\n⏱️ Simulating {3} monitoring cycles...")
        
        for cycle in range(3):
            print(f"\n🔄 Cycle {cycle + 1}/3 - {datetime.now().strftime('%H:%M:%S')}")
            
            # In a real scenario, the scheduler would automatically:
            # 1. Check prices for all tracked stocks
            # 2. Compare with previous prices
            # 3. Generate alerts for significant changes
            # 4. Send SMS notifications
            
            print("   📊 Checking stock prices...")
            print("   🔍 Comparing with previous prices...")
            print("   🤖 Generating AI analysis for changes...")
            print("   📱 Sending alerts if thresholds exceeded...")
            
            # Wait between cycles (in real scenario, this would be automatic)
            if cycle < 2:  # Don't wait after the last cycle
                print("   ⏳ Waiting for next cycle...")
                await asyncio.sleep(3)  # Short wait for demo
        
        print(f"\n✅ Completed {3} monitoring cycles")
        print("📋 Check the mock SMS output above for any alerts that were generated")
        
    except Exception as e:
        print(f"❌ Error testing scheduler: {str(e)}")
    finally:
        # Stop the scheduler
        print("\n🛑 Stopping scheduler...")
        try:
            await scheduler_service.stop()
            print("✅ Scheduler stopped successfully")
        except Exception as e:
            print(f"⚠️ Error stopping scheduler: {str(e)}")


async def test_manual_stock_check():
    """
    Test manual stock checking (simulating what the scheduler does).
    
    This function manually performs the same operations that the scheduler
    would do automatically, so you can see exactly what happens.
    """
    print("🚀 Manual Stock Check Test")
    print("=" * 40)
    
    # Initialize services
    print("🔄 Initializing services...")
    stock_service = StockService()
    sms_service = MockSMSService()
    agent_service = AgentService()
    
    # Test stocks
    test_stocks = ["AAPL", "TSLA"]
    print(f"📋 Checking stocks: {', '.join(test_stocks)}")
    
    for symbol in test_stocks:
        try:
            print(f"\n🔍 Checking {symbol}...")
            
            # Get current stock info
            stock_info = await stock_service.get_stock_info(symbol)
            if not stock_info:
                print(f"   ❌ Could not fetch data for {symbol}")
                continue
            
            current_price = stock_info.get('current_price', 0)
            print(f"   💰 Current price: ${current_price}")
            
            if current_price > 0:
                # Simulate a price change that would trigger an alert
                # (assuming we had a previous price to compare with)
                previous_price = current_price * 0.94  # Simulate 6% increase
                change_percent = 6.0
                
                print(f"   📊 Simulating price change: ${previous_price:.2f} → ${current_price:.2f}")
                print(f"   📈 Change: {change_percent:+.2f}%")
                
                # Check if this would trigger an alert
                if abs(change_percent) >= settings.alert_threshold_percent:
                    print(f"   🚨 Alert triggered! ({change_percent:+.2f}% > {settings.alert_threshold_percent}%)")
                    
                    # Generate AI analysis
                    print(f"   🤖 Generating AI analysis...")
                    analysis = await agent_service.analyze_stock_movement(
                        symbol, previous_price, current_price
                    )
                    
                    # Generate alert message
                    print(f"   📝 Creating alert message...")
                    # Create a simple alert message for testing
                    change_amount = current_price - previous_price
                    alert_message = f"📈 {symbol} Alert\n\nPrice: ${current_price:.2f} ({change_percent:+.2f}%)\nPrevious: ${previous_price:.2f}\n\n{analysis.analysis}\n\nKey factors: {', '.join(analysis.key_factors[:3])}"
                    
                    # Send alert
                    print(f"   📱 Sending alert...")
                    await sms_service.send_sms(
                        to_number=settings.user_phone_number,
                        message=alert_message,
                        message_type="alert"
                    )
                    
                    print(f"   ✅ Alert sent for {symbol}")
                else:
                    print(f"   ✅ No alert needed ({change_percent:+.2f}% < {settings.alert_threshold_percent}%)")
            
        except Exception as e:
            print(f"   ❌ Error checking {symbol}: {str(e)}")


async def main():
    """Main function with menu options."""
    print("🎯 Scheduler Testing")
    print("Choose a test:")
    print("1. Test background scheduler")
    print("2. Test manual stock checking")
    print("3. Both tests")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            await test_scheduler()
        elif choice == "2":
            await test_manual_stock_check()
        elif choice == "3":
            await test_scheduler()
            print("\n" + "="*50)
            await test_manual_stock_check()
        else:
            print("❌ Invalid choice. Running scheduler test...")
            await test_scheduler()
            
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
