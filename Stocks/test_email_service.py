#!/usr/bin/env python3
"""
Email Service Test Script

This script tests the EmailService functionality to ensure it works correctly
before deploying to the cloud. It tests both mock mode and real email sending.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, 'app')

from app.services.email_service import EmailService
from app.models.config import settings

async def test_email_service():
    """Test the email service functionality"""
    print("📧 Email Service Test")
    print("=" * 50)
    
    # Initialize email service
    print("🔄 Initializing EmailService...")
    email_service = EmailService()
    
    if email_service.is_mock_mode:
        print("✅ Running in MOCK mode (emails will be logged to console)")
        print("   To enable real emails, configure SMTP settings in your .env file")
    else:
        print("✅ Running in REAL mode (emails will be sent via SMTP)")
    
    print()
    
    # Test 1: Basic email sending
    print("🧪 Test 1: Basic Email Sending")
    print("-" * 30)
    
    html_content = """
    <html>
    <body>
        <h1>Test Email</h1>
        <p>This is a test email from the AI Stock Tracking Agent.</p>
        <p>Time: {}</p>
    </body>
    </html>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    text_content = "Test Email\n\nThis is a test email from the AI Stock Tracking Agent.\nTime: {}".format(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    
    result = await email_service.send_email(
        to_email=settings.to_email or "test@example.com",
        subject="🧪 Test Email from Stock Agent",
        html_content=html_content,
        text_content=text_content,
        message_type="test"
    )
    
    if result:
        print("✅ Basic email test passed")
    else:
        print("❌ Basic email test failed")
    
    print()
    
    # Test 2: Stock alert email
    print("🧪 Test 2: Stock Alert Email")
    print("-" * 30)
    
    result = await email_service.send_stock_alert(
        symbol="AAPL",
        current_price=229.50,
        previous_price=232.14,
        change_percent=-1.14,
        analysis="Apple Inc. stock decreased by 1.14% due to market conditions and profit-taking by investors. This appears to be a normal market correction and does not indicate any fundamental issues with the company.",
        key_factors=[
            "Market conditions",
            "Profit-taking by investors", 
            "Normal market correction"
        ],
        alert_type="DAILY"
    )
    
    if result:
        print("✅ Stock alert email test passed")
    else:
        print("❌ Stock alert email test failed")
    
    print()
    
    # Test 3: Positive stock alert
    print("🧪 Test 3: Positive Stock Alert")
    print("-" * 30)
    
    result = await email_service.send_stock_alert(
        symbol="MSTY",
        current_price=15.85,
        previous_price=15.50,
        change_percent=2.26,
        analysis="MSTY (Yieldmax MSTR Option Income Strategy ETF) increased by 2.26% due to strong investor interest and positive market sentiment. This indicates growing confidence in the underlying strategy and market conditions.",
        key_factors=[
            "Strong investor interest",
            "Positive market sentiment",
            "Growing confidence in strategy"
        ],
        alert_type="DAILY"
    )
    
    if result:
        print("✅ Positive stock alert test passed")
    else:
        print("❌ Positive stock alert test failed")
    
    print()
    
    # Test 4: Check message history
    print("🧪 Test 4: Message History")
    print("-" * 30)
    
    history = email_service.get_message_history()
    print(f"📊 Total emails sent: {len(history)}")
    
    for i, msg in enumerate(history, 1):
        print(f"   {i}. {msg.subject} ({msg.message_type}) - {msg.timestamp.strftime('%H:%M:%S')}")
    
    print()
    
    # Test 5: Configuration check
    print("🧪 Test 5: Configuration Check")
    print("-" * 30)
    
    print(f"📧 SMTP Server: {settings.smtp_server or 'Not configured'}")
    print(f"📧 SMTP Port: {settings.smtp_port}")
    print(f"📧 SMTP Username: {settings.smtp_username or 'Not configured'}")
    print(f"📧 From Email: {settings.from_email or 'Not configured'}")
    print(f"📧 To Email: {settings.to_email or 'Not configured'}")
    
    if email_service.is_mock_mode:
        print("\n💡 To enable real emails, add these to your .env file:")
        print("   SMTP_SERVER=smtp.gmail.com")
        print("   SMTP_PORT=587")
        print("   SMTP_USERNAME=your-email@gmail.com")
        print("   SMTP_PASSWORD=your-app-password")
        print("   FROM_EMAIL=your-email@gmail.com")
        print("   TO_EMAIL=your-email@gmail.com")
    
    print()
    print("✅ Email service testing completed!")
    
    if email_service.is_mock_mode:
        print("\n📝 Note: All emails were sent in MOCK mode and logged to console.")
        print("   To send real emails, configure SMTP settings in your .env file.")

async def main():
    """Main function to run the email tests"""
    await test_email_service()

if __name__ == "__main__":
    asyncio.run(main())
