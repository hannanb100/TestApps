#!/usr/bin/env python3
"""
Automated Alert Testing System for AI Stock Tracking Agent.

This script provides multiple ways to test the automated alert system:
1. Test with real stock data (live prices)
2. Test with simulated price changes
3. Test the background scheduler
4. Test alert generation and SMS sending

For beginners: This script helps you verify that your alert system works
correctly by simulating different scenarios and checking real stock prices.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.mock_sms_service import MockSMSService
from app.services.stock_service import StockService
from app.services.agent_service import AgentService
from app.services.scheduler_service import SchedulerService
from app.models.config import settings


class AlertTester:
    """
    Comprehensive alert testing system.
    
    This class provides multiple testing methods to verify that your
    automated alert system works correctly in different scenarios.
    """
    
    def __init__(self):
        """Initialize the alert testing system."""
        print("🚀 Initializing Alert Testing System...")
        
        # Initialize all services
        self.stock_service = StockService()
        self.sms_service = MockSMSService()
        self.agent_service = AgentService()
        self.scheduler_service = SchedulerService(
            stock_service=self.stock_service,
            agent_service=self.agent_service,
            sms_service=self.sms_service
        )
        
        print("✅ All services initialized successfully!")
    
    async def test_real_stock_alerts(self):
        """
        Test alerts with real stock data.
        
        This method fetches real stock prices and simulates price changes
        to test the alert system with actual market data.
        """
        print("\n" + "="*60)
        print("📊 TESTING REAL STOCK ALERTS")
        print("="*60)
        
        # Test stocks with different volatility levels
        test_stocks = [
            "AAPL",  # Apple - generally stable
            "TSLA",  # Tesla - more volatile
            "NVDA",  # NVIDIA - tech stock
            "SPY",   # S&P 500 ETF - market index
        ]
        
        for symbol in test_stocks:
            try:
                print(f"\n🔍 Testing {symbol}...")
                
                # Get current stock data
                stock_info = await self.stock_service.get_stock_info(symbol)
                if not stock_info:
                    print(f"❌ Could not fetch data for {symbol}")
                    continue
                
                current_price = stock_info.get('current_price', 0)
                print(f"📈 Current price: ${current_price}")
                
                # Simulate a price change that would trigger an alert
                # (assuming 5% threshold from settings)
                threshold = settings.alert_threshold_percent
                change_percent = threshold + 1  # Just above threshold
                
                if current_price > 0:
                    # Calculate new price that would trigger alert
                    price_change = current_price * (change_percent / 100)
                    new_price = current_price + price_change
                    
                    print(f"🎯 Simulating {change_percent:.1f}% price change")
                    print(f"📊 New price: ${new_price:.2f} (was ${current_price:.2f})")
                    
                    # Test the alert generation
                    await self._test_alert_generation(
                        symbol, current_price, new_price, change_percent
                    )
                
            except Exception as e:
                print(f"❌ Error testing {symbol}: {str(e)}")
    
    async def test_simulated_alerts(self):
        """
        Test alerts with completely simulated data.
        
        This method creates fake price changes to test the alert system
        without relying on real market data.
        """
        print("\n" + "="*60)
        print("🎭 TESTING SIMULATED ALERTS")
        print("="*60)
        
        # Test different scenarios
        test_scenarios = [
            {
                "symbol": "TEST1",
                "name": "Test Stock 1",
                "previous_price": 100.00,
                "current_price": 106.00,  # +6% change
                "description": "Moderate positive change"
            },
            {
                "symbol": "TEST2", 
                "name": "Test Stock 2",
                "previous_price": 50.00,
                "current_price": 47.50,  # -5% change
                "description": "Moderate negative change"
            },
            {
                "symbol": "TEST3",
                "name": "Test Stock 3", 
                "previous_price": 200.00,
                "current_price": 220.00,  # +10% change
                "description": "Large positive change"
            },
            {
                "symbol": "TEST4",
                "name": "Test Stock 4",
                "previous_price": 75.00,
                "current_price": 67.50,  # -10% change
                "description": "Large negative change"
            }
        ]
        
        for scenario in test_scenarios:
            try:
                print(f"\n🎯 Testing scenario: {scenario['description']}")
                print(f"📊 {scenario['symbol']}: ${scenario['previous_price']} → ${scenario['current_price']}")
                
                # Calculate percentage change
                change = scenario['current_price'] - scenario['previous_price']
                change_percent = (change / scenario['previous_price']) * 100
                
                print(f"📈 Change: {change_percent:+.2f}%")
                
                # Test alert generation
                await self._test_alert_generation(
                    scenario['symbol'],
                    scenario['previous_price'],
                    scenario['current_price'],
                    change_percent
                )
                
            except Exception as e:
                print(f"❌ Error in scenario {scenario['symbol']}: {str(e)}")
    
    async def _test_alert_generation(self, symbol: str, previous_price: float, 
                                   current_price: float, change_percent: float):
        """
        Test the alert generation process for a specific stock.
        
        Args:
            symbol: Stock symbol
            previous_price: Previous stock price
            current_price: Current stock price
            change_percent: Percentage change
        """
        try:
            print(f"🤖 Generating AI analysis for {symbol}...")
            
            # Generate AI analysis
            analysis = await self.agent_service.analyze_stock_movement(
                symbol, previous_price, current_price
            )
            
            print(f"✅ Analysis generated:")
            print(f"   📝 Analysis: {analysis.analysis[:100]}...")
            print(f"   🎯 Confidence: {analysis.confidence_score:.2f}")
            print(f"   🔑 Key factors: {', '.join(analysis.key_factors[:3])}")
            
            # Test alert message generation
            print(f"📱 Generating alert message...")
            # Create a simple alert message for testing
            change_amount = current_price - previous_price
            alert_message = f"📈 {symbol} Alert\n\nPrice: ${current_price:.2f} ({change_percent:+.2f}%)\nPrevious: ${previous_price:.2f}\n\n{analysis.analysis}\n\nKey factors: {', '.join(analysis.key_factors[:3])}"
            
            print(f"✅ Alert message generated:")
            print(f"   📄 Message: {alert_message[:150]}...")
            
            # Send mock SMS alert
            print(f"📲 Sending mock SMS alert...")
            await self.sms_service.send_sms(
                to_number=settings.user_phone_number,
                message=alert_message,
                message_type="alert"
            )
            
            print(f"✅ Alert test completed for {symbol}")
            
        except Exception as e:
            print(f"❌ Error generating alert for {symbol}: {str(e)}")
    
    async def test_scheduler_integration(self):
        """
        Test the background scheduler with alert functionality.
        
        This method tests how the scheduler would work in a real scenario.
        """
        print("\n" + "="*60)
        print("⏰ TESTING SCHEDULER INTEGRATION")
        print("="*60)
        
        try:
            # Start the scheduler
            print("🔄 Starting scheduler...")
            await self.scheduler_service.start()
            
            # Add some test stocks to track
            test_stocks = ["AAPL", "TSLA", "GOOGL"]
            print(f"📋 Adding test stocks: {', '.join(test_stocks)}")
            
            # Simulate the scheduler running for a few cycles
            print("⏱️ Simulating scheduler cycles...")
            for i in range(3):
                print(f"\n🔄 Cycle {i+1}/3")
                
                # Simulate stock price check
                for symbol in test_stocks:
                    try:
                        # Get current price
                        stock_info = await self.stock_service.get_stock_info(symbol)
                        if stock_info:
                            current_price = stock_info.get('current_price', 0)
                            print(f"   📊 {symbol}: ${current_price}")
                            
                            # Simulate a price change (random for testing)
                            if current_price > 0:
                                change_percent = random.uniform(-8, 8)  # Random change between -8% and +8%
                                new_price = current_price * (1 + change_percent / 100)
                                
                                # Check if this would trigger an alert
                                if abs(change_percent) >= settings.alert_threshold_percent:
                                    print(f"   🚨 Alert triggered! {change_percent:+.2f}% change")
                                    await self._test_alert_generation(
                                        symbol, current_price, new_price, change_percent
                                    )
                                else:
                                    print(f"   ✅ No alert needed ({change_percent:+.2f}% change)")
                        
                    except Exception as e:
                        print(f"   ❌ Error checking {symbol}: {str(e)}")
                
                # Wait a bit between cycles
                await asyncio.sleep(2)
            
            # Stop the scheduler
            print("\n🛑 Stopping scheduler...")
            await self.scheduler_service.stop()
            
        except Exception as e:
            print(f"❌ Error testing scheduler: {str(e)}")
    
    async def test_alert_thresholds(self):
        """
        Test different alert threshold scenarios.
        
        This method tests how the system behaves with different
        price change percentages.
        """
        print("\n" + "="*60)
        print("🎯 TESTING ALERT THRESHOLDS")
        print("="*60)
        
        base_price = 100.00
        test_symbol = "THRESHOLD_TEST"
        
        # Test different percentage changes
        test_changes = [
            {"percent": 2.0, "should_alert": False, "description": "Below threshold"},
            {"percent": 4.9, "should_alert": False, "description": "Just below threshold"},
            {"percent": 5.0, "should_alert": True, "description": "Exactly at threshold"},
            {"percent": 5.1, "should_alert": True, "description": "Just above threshold"},
            {"percent": 10.0, "should_alert": True, "description": "Well above threshold"},
            {"percent": -3.0, "should_alert": False, "description": "Small negative change"},
            {"percent": -5.0, "should_alert": True, "description": "Negative threshold"},
            {"percent": -10.0, "should_alert": True, "description": "Large negative change"},
        ]
        
        for test in test_changes:
            try:
                new_price = base_price * (1 + test["percent"] / 100)
                
                print(f"\n🧪 Testing {test['description']}: {test['percent']:+.1f}%")
                print(f"   💰 Price: ${base_price:.2f} → ${new_price:.2f}")
                
                # Check if this should trigger an alert
                would_alert = abs(test["percent"]) >= settings.alert_threshold_percent
                
                if would_alert == test["should_alert"]:
                    print(f"   ✅ Correct behavior: {'Would alert' if would_alert else 'No alert'}")
                    
                    if would_alert:
                        await self._test_alert_generation(
                            test_symbol, base_price, new_price, test["percent"]
                        )
                else:
                    print(f"   ❌ Unexpected behavior: {'Would alert' if would_alert else 'No alert'}")
                
            except Exception as e:
                print(f"   ❌ Error in threshold test: {str(e)}")
    
    def show_test_summary(self):
        """Show a summary of all tests and their results."""
        print("\n" + "="*60)
        print("📋 TEST SUMMARY")
        print("="*60)
        
        # Get SMS history
        history = self.sms_service.get_message_history()
        
        print(f"📱 Total mock SMS messages sent: {len(history)}")
        print(f"🎯 Alert threshold: {settings.alert_threshold_percent}%")
        print(f"⏰ Check interval: {settings.check_interval_minutes} minutes")
        
        if history:
            print(f"\n📄 Recent messages:")
            for i, msg in enumerate(history[-5:], 1):  # Show last 5 messages
                print(f"   {i}. [{msg['time']}] {msg['type'].upper()}: {msg['message'][:80]}...")
        
        print(f"\n✅ Testing completed! Check the mock SMS output above to see alerts.")
        print(f"💡 To test with real data, run this script during market hours.")
    
    async def run_all_tests(self):
        """Run all available tests."""
        print("🚀 AI Stock Tracking Agent - Alert Testing Suite")
        print("=" * 60)
        
        try:
            # Run all test suites
            await self.test_simulated_alerts()
            await self.test_alert_thresholds()
            await self.test_real_stock_alerts()
            await self.test_scheduler_integration()
            
            # Show summary
            self.show_test_summary()
            
        except Exception as e:
            print(f"❌ Error running tests: {str(e)}")
        finally:
            # Cleanup
            if hasattr(self, 'scheduler_service'):
                try:
                    await self.scheduler_service.stop()
                except:
                    pass


async def main():
    """Main entry point for alert testing."""
    print("🎯 Alert Testing System")
    print("Choose a test option:")
    print("1. Run all tests")
    print("2. Test simulated alerts only")
    print("3. Test real stock alerts only")
    print("4. Test scheduler integration only")
    print("5. Test alert thresholds only")
    
    try:
        choice = input("\nEnter your choice (1-5): ").strip()
        
        tester = AlertTester()
        
        if choice == "1":
            await tester.run_all_tests()
        elif choice == "2":
            await tester.test_simulated_alerts()
            tester.show_test_summary()
        elif choice == "3":
            await tester.test_real_stock_alerts()
            tester.show_test_summary()
        elif choice == "4":
            await tester.test_scheduler_integration()
            tester.show_test_summary()
        elif choice == "5":
            await tester.test_alert_thresholds()
            tester.show_test_summary()
        else:
            print("❌ Invalid choice. Running all tests...")
            await tester.run_all_tests()
            
    except KeyboardInterrupt:
        print("\n👋 Testing interrupted by user")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
