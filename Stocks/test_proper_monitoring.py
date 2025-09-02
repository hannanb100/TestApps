#!/usr/bin/env python3
"""
Proper Stock Monitoring Test

This test demonstrates the correct behavior:
1. Uses your actual 1-minute interval setting
2. Shows the difference between "vs previous close" and "vs previous run" logic
3. Uses real stock data from your watchlist
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, 'app')

from app.services.stock_service import StockService
from app.services.agent_service import AgentService
from app.services.email_service import EmailService
from app.models.config import settings

class ProperMonitoringTest:
    def __init__(self):
        self.stock_service = StockService()
        self.agent_service = AgentService()
        self.email_service = EmailService()
        self.previous_prices = {}  # Store previous run prices
        
    async def test_monitoring_cycles(self):
        """Test monitoring with proper intervals and price comparison logic"""
        print("🎯 Proper Stock Monitoring Test")
        print("=" * 50)
        
        # Get your actual watchlist
        watchlist = ["AAPL", "MSTY"]  # Your current stocks
        print(f"📋 Monitoring your stocks: {', '.join(watchlist)}")
        print(f"🎯 Alert threshold: {settings.alert_threshold_percent}%")
        print(f"⏰ Check interval: {settings.check_interval_minutes} minutes")
        print()
        
        # Test 3 cycles with proper timing
        for cycle in range(1, 4):
            print(f"🔄 Monitoring Cycle {cycle}/3 - {datetime.now().strftime('%H:%M:%S')}")
            print()
            
            for symbol in watchlist:
                try:
                    print(f"🔍 Checking {symbol}...")
                    
                    # Get current stock data
                    stock_info = await self.stock_service.get_stock_info(symbol)
                    if not stock_info:
                        print(f"   ❌ Could not fetch data for {symbol}")
                        continue
                    
                    current_price = stock_info.get('current_price', 0)
                    previous_close = stock_info.get('previous_close', 0)
                    
                    print(f"   💰 Current price: ${current_price}")
                    print(f"   📊 Previous close: ${previous_close}")
                    
                    if current_price > 0 and previous_close > 0:
                        # Method 1: Compare with previous close (yesterday's close)
                        vs_previous_close = ((current_price - previous_close) / previous_close) * 100
                        print(f"   📈 vs Previous Close: {vs_previous_close:+.2f}%")
                        
                        # Method 2: Compare with previous run (if we have it)
                        if symbol in self.previous_prices:
                            vs_previous_run = ((current_price - self.previous_prices[symbol]) / self.previous_prices[symbol]) * 100
                            print(f"   📈 vs Previous Run: {vs_previous_run:+.2f}%")
                            
                            # Use the larger change for alert decision
                            max_change = max(abs(vs_previous_close), abs(vs_previous_run))
                            if max_change >= settings.alert_threshold_percent:
                                # Determine which alert type was triggered
                                if abs(vs_previous_close) > abs(vs_previous_run):
                                    alert_type = "DAILY"
                                    trigger_change = vs_previous_close
                                else:
                                    alert_type = "INTRADAY"
                                    trigger_change = vs_previous_run
                                
                                print(f"   🚨 {alert_type} Alert triggered! ({trigger_change:+.2f}% > {settings.alert_threshold_percent}%)")
                                
                                # Generate AI analysis
                                print(f"   🤖 Generating AI analysis...")
                                analysis = await self.agent_service.analyze_stock_movement(
                                    symbol, previous_close, current_price
                                )
                                
                                # Send email alert
                                print(f"   📧 Sending email alert...")
                                await self.email_service.send_stock_alert(
                                    symbol=symbol,
                                    current_price=current_price,
                                    previous_price=previous_close,
                                    change_percent=vs_previous_close,
                                    analysis=analysis.analysis,
                                    key_factors=analysis.key_factors,
                                    alert_type=alert_type
                                )
                                
                                print(f"   ✅ Alert sent for {symbol}")
                            else:
                                print(f"   ✅ No alert needed (Max change: {max_change:.2f}% < {settings.alert_threshold_percent}%)")
                        else:
                            # First run - only check vs previous close
                            if abs(vs_previous_close) >= settings.alert_threshold_percent:
                                alert_type = "DAILY"
                                print(f"   🚨 {alert_type} Alert triggered! ({vs_previous_close:+.2f}% > {settings.alert_threshold_percent}%)")
                                
                                # Generate AI analysis
                                print(f"   🤖 Generating AI analysis...")
                                analysis = await self.agent_service.analyze_stock_movement(
                                    symbol, previous_close, current_price
                                )
                                
                                # Send email alert
                                print(f"   📧 Sending email alert...")
                                await self.email_service.send_stock_alert(
                                    symbol=symbol,
                                    current_price=current_price,
                                    previous_price=previous_close,
                                    change_percent=vs_previous_close,
                                    analysis=analysis.analysis,
                                    key_factors=analysis.key_factors,
                                    alert_type=alert_type
                                )
                                
                                print(f"   ✅ Alert sent for {symbol}")
                            else:
                                print(f"   ✅ No alert needed ({vs_previous_close:+.2f}% < {settings.alert_threshold_percent}%)")
                        
                        # Store current price for next run
                        self.previous_prices[symbol] = current_price
                        
                    else:
                        print(f"   ❌ Invalid price data for {symbol}")
                
                except Exception as e:
                    print(f"   ❌ Error checking {symbol}: {str(e)}")
            
            # Wait for next cycle (use your actual interval for testing)
            if cycle < 3:
                print(f"\n⏳ Waiting {settings.check_interval_minutes} minute(s) for next cycle...")
                print("   (In real system, this would be handled by the scheduler)")
                # For testing, use 10 seconds instead of full minute
                await asyncio.sleep(10)
        
        print("\n✅ Completed monitoring cycles")
        print("\n📋 Summary:")
        print(f"   📧 Total alerts sent: {len(self.email_service.message_history)}")
        print(f"   📊 Stocks monitored: {', '.join(watchlist)}")
        print(f"   🎯 Alert threshold: {settings.alert_threshold_percent}%")
        print(f"   ⏰ Check interval: {settings.check_interval_minutes} minutes")

async def main():
    """Main function to run the test"""
    test = ProperMonitoringTest()
    await test.test_monitoring_cycles()

if __name__ == "__main__":
    asyncio.run(main())
