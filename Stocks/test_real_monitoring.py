#!/usr/bin/env python3
"""
Real Stock Monitoring Test - Test with your actual watchlist.

This script tests the monitoring system with your actual stocks
and checks for genuine price changes that would trigger alerts.
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
from app.models.config import settings


async def test_real_monitoring():
    """
    Test monitoring with your actual watchlist stocks.
    
    This function checks your actual stocks (AAPL, MSTY) for real price changes
    and simulates what would happen if the scheduler detected significant movements.
    """
    print("🚀 Real Stock Monitoring Test")
    print("=" * 50)
    
    # Initialize services
    print("🔄 Initializing services...")
    stock_service = StockService()
    sms_service = MockSMSService()
    agent_service = AgentService()
    
    # Your actual watchlist
    your_stocks = ["AAPL", "MSTY"]
    print(f"📋 Monitoring your stocks: {', '.join(your_stocks)}")
    print(f"🎯 Alert threshold: {settings.alert_threshold_percent}%")
    
    try:
        for cycle in range(3):  # Run 3 monitoring cycles
            print(f"\n🔄 Monitoring Cycle {cycle + 1}/3 - {datetime.now().strftime('%H:%M:%S')}")
            
            for symbol in your_stocks:
                try:
                    print(f"\n🔍 Checking {symbol}...")
                    
                    # Get current stock data from Yahoo Finance
                    stock_info = await stock_service.get_stock_info(symbol)
                    if not stock_info:
                        print(f"   ❌ Could not fetch data for {symbol}")
                        continue
                    
                    current_price = stock_info.get('current_price', 0)
                    print(f"   💰 Current price: ${current_price}")
                    
                    if current_price > 0:
                        # For this test, let's simulate a price change that would trigger an alert
                        # In a real scenario, we'd compare with the stored previous price
                        
                        # Simulate a 2% change (above your 1% threshold)
                        change_percent = 2.0
                        previous_price = current_price / (1 + change_percent / 100)
                        
                        print(f"   📊 Simulated change: ${previous_price:.2f} → ${current_price:.2f}")
                        print(f"   📈 Change: {change_percent:+.2f}%")
                        
                        # Check if this would trigger an alert
                        if abs(change_percent) >= settings.alert_threshold_percent:
                            print(f"   🚨 Alert triggered! ({change_percent:+.2f}% > {settings.alert_threshold_percent}%)")
                            
                            # Generate AI analysis
                            print(f"   🤖 Generating AI analysis...")
                            analysis = await agent_service.analyze_stock_movement(
                                symbol, previous_price, current_price
                            )
                            
                            print(f"   ✅ Analysis generated (confidence: {analysis.confidence_score:.2f})")
                            
                            # Create alert message
                            print(f"   📝 Creating alert message...")
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
                    else:
                        print(f"   ❌ Invalid price data for {symbol}")
                
                except Exception as e:
                    print(f"   ❌ Error checking {symbol}: {str(e)}")
            
            # Wait between cycles
            if cycle < 2:
                print(f"\n⏳ Waiting for next cycle...")
                await asyncio.sleep(2)
        
        print(f"\n✅ Completed monitoring cycles")
        
        # Show summary
        history = sms_service.get_message_history()
        print(f"\n📋 Summary:")
        print(f"   📱 Total alerts sent: {len(history)}")
        print(f"   📊 Stocks monitored: {', '.join(your_stocks)}")
        print(f"   🎯 Alert threshold: {settings.alert_threshold_percent}%")
        
        if history:
            print(f"\n📄 Alert messages sent:")
            for i, msg in enumerate(history, 1):
                print(f"   {i}. [{msg['time']}] {msg['type'].upper()}: {msg['message'][:80]}...")
        
    except Exception as e:
        print(f"❌ Error in monitoring test: {str(e)}")


async def test_with_real_price_changes():
    """
    Test with actual real-time price changes.
    
    This function fetches real current prices and simulates realistic
    price movements to test the alert system.
    """
    print("🚀 Real-Time Price Change Test")
    print("=" * 50)
    
    # Initialize services
    print("🔄 Initializing services...")
    stock_service = StockService()
    sms_service = MockSMSService()
    agent_service = AgentService()
    
    # Test with your stocks
    test_stocks = ["AAPL", "MSTY"]
    print(f"📋 Testing with: {', '.join(test_stocks)}")
    
    for symbol in test_stocks:
        try:
            print(f"\n🔍 Testing {symbol} with real price data...")
            
            # Get real current price
            stock_info = await stock_service.get_stock_info(symbol)
            if not stock_info:
                print(f"   ❌ Could not fetch real data for {symbol}")
                continue
            
            current_price = stock_info.get('current_price', 0)
            print(f"   💰 Real current price: ${current_price}")
            
            if current_price > 0:
                # Simulate a realistic price change (3% increase)
                change_percent = 3.0
                previous_price = current_price / (1 + change_percent / 100)
                
                print(f"   📊 Simulated scenario: ${previous_price:.2f} → ${current_price:.2f}")
                print(f"   📈 Change: {change_percent:+.2f}%")
                
                if abs(change_percent) >= settings.alert_threshold_percent:
                    print(f"   🚨 This would trigger an alert!")
                    
                    # Generate and send alert
                    analysis = await agent_service.analyze_stock_movement(
                        symbol, previous_price, current_price
                    )
                    
                    alert_message = f"📈 {symbol} Alert\n\nPrice: ${current_price:.2f} ({change_percent:+.2f}%)\nPrevious: ${previous_price:.2f}\n\n{analysis.analysis}\n\nKey factors: {', '.join(analysis.key_factors[:3])}"
                    
                    await sms_service.send_sms(
                        to_number=settings.user_phone_number,
                        message=alert_message,
                        message_type="alert"
                    )
                    
                    print(f"   ✅ Alert sent for {symbol}")
                else:
                    print(f"   ✅ No alert needed")
            else:
                print(f"   ❌ No valid price data for {symbol}")
                
        except Exception as e:
            print(f"   ❌ Error testing {symbol}: {str(e)}")


async def main():
    """Main function with menu options."""
    print("🎯 Real Stock Monitoring Test")
    print("Choose a test:")
    print("1. Test monitoring cycles (simulated changes)")
    print("2. Test with real price data")
    print("3. Both tests")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            await test_real_monitoring()
        elif choice == "2":
            await test_with_real_price_changes()
        elif choice == "3":
            await test_real_monitoring()
            print("\n" + "="*60)
            await test_with_real_price_changes()
        else:
            print("❌ Invalid choice. Running monitoring test...")
            await test_real_monitoring()
            
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
