#!/usr/bin/env python3
"""
Quick Alert Test - Simple way to test automated alerts.

This script provides a quick and easy way to test your alert system
without running the full test suite. Perfect for quick verification!
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


async def quick_alert_test():
    """
    Quick test of the alert system with a simulated price change.
    
    This function simulates a stock price change that would trigger an alert
    and shows you exactly what the user would receive via SMS.
    """
    print("🚀 Quick Alert Test")
    print("=" * 40)
    
    # Initialize services
    print("🔄 Initializing services...")
    stock_service = StockService()
    sms_service = MockSMSService()
    agent_service = AgentService()
    
    # Test parameters
    symbol = "AAPL"  # Apple stock
    previous_price = 150.00  # Previous price
    current_price = 157.50   # New price (5% increase)
    
    print(f"📊 Testing alert for {symbol}")
    print(f"💰 Price change: ${previous_price} → ${current_price}")
    
    # Calculate percentage change
    change_percent = ((current_price - previous_price) / previous_price) * 100
    print(f"📈 Change: {change_percent:+.2f}%")
    print(f"🎯 Alert threshold: {settings.alert_threshold_percent}%")
    
    if abs(change_percent) >= settings.alert_threshold_percent:
        print("🚨 This change would trigger an alert!")
        
        try:
            # Generate AI analysis
            print("\n🤖 Generating AI analysis...")
            analysis = await agent_service.analyze_stock_movement(
                symbol, previous_price, current_price
            )
            
            print(f"✅ Analysis generated (confidence: {analysis.confidence_score:.2f})")
            
            # Generate alert message
            print("📝 Creating alert message...")
            # Create a simple alert message for testing
            change_amount = current_price - previous_price
            alert_message = f"📈 {symbol} Alert\n\nPrice: ${current_price:.2f} ({change_percent:+.2f}%)\nPrevious: ${previous_price:.2f}\n\n{analysis.analysis}\n\nKey factors: {', '.join(analysis.key_factors[:3])}"
            
            # Send mock SMS
            print("📱 Sending mock SMS alert...")
            await sms_service.send_sms(
                to_number=settings.user_phone_number,
                message=alert_message,
                message_type="alert"
            )
            
            print("\n✅ Alert test completed!")
            print("📋 Check the mock SMS output above to see what the user would receive.")
            
        except Exception as e:
            print(f"❌ Error generating alert: {str(e)}")
    else:
        print("✅ This change would NOT trigger an alert (below threshold)")


async def test_real_stock():
    """
    Test with a real stock price.
    
    This function fetches a real stock price and simulates a change
    to test the alert system with actual market data.
    """
    print("🚀 Real Stock Alert Test")
    print("=" * 40)
    
    # Initialize services
    print("🔄 Initializing services...")
    stock_service = StockService()
    sms_service = MockSMSService()
    agent_service = AgentService()
    
    # Get a real stock price
    symbol = "AAPL"  # You can change this to any stock symbol
    
    try:
        print(f"📊 Fetching real price for {symbol}...")
        stock_info = await stock_service.get_stock_info(symbol)
        
        if not stock_info:
            print(f"❌ Could not fetch data for {symbol}")
            return
        
        current_price = stock_info.get('current_price', 0)
        print(f"💰 Current price: ${current_price}")
        
        if current_price > 0:
            # Simulate a 6% increase (above the 5% threshold)
            new_price = current_price * 1.06
            change_percent = 6.0
            
            print(f"🎯 Simulating 6% price increase")
            print(f"📈 New price: ${new_price:.2f}")
            
            # Generate alert
            print("\n🤖 Generating AI analysis...")
            analysis = await agent_service.analyze_stock_movement(
                symbol, current_price, new_price
            )
            
            print(f"✅ Analysis generated (confidence: {analysis.confidence_score:.2f})")
            
            # Generate and send alert
            print("📝 Creating alert message...")
            # Create a simple alert message for testing
            change_amount = new_price - current_price
            alert_message = f"📈 {symbol} Alert\n\nPrice: ${new_price:.2f} ({change_percent:+.2f}%)\nPrevious: ${current_price:.2f}\n\n{analysis.analysis}\n\nKey factors: {', '.join(analysis.key_factors[:3])}"
            
            print("📱 Sending mock SMS alert...")
            await sms_service.send_sms(
                to_number=settings.user_phone_number,
                message=alert_message,
                message_type="alert"
            )
            
            print("\n✅ Real stock alert test completed!")
            
        else:
            print("❌ Invalid price data received")
            
    except Exception as e:
        print(f"❌ Error testing real stock: {str(e)}")


async def main():
    """Main function with menu options."""
    print("🎯 Quick Alert Testing")
    print("Choose a test:")
    print("1. Simulated alert test (quick)")
    print("2. Real stock test (requires internet)")
    print("3. Both tests")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            await quick_alert_test()
        elif choice == "2":
            await test_real_stock()
        elif choice == "3":
            await quick_alert_test()
            print("\n" + "="*50)
            await test_real_stock()
        else:
            print("❌ Invalid choice. Running simulated test...")
            await quick_alert_test()
            
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
