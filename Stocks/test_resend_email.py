#!/usr/bin/env python3
"""
Test Resend email service locally
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.email_service import EmailService

async def test_resend_email():
    print("=== Testing Resend Email Service ===")
    
    # Initialize email service
    email_service = EmailService()
    
    print(f"1. Mock mode: {email_service.is_mock_mode}")
    print(f"2. From email: {email_service.from_email}")
    print(f"3. To email: {email_service.to_email}")
    print(f"4. Resend API key set: {bool(email_service.resend_api_key)}")
    
    if email_service.is_mock_mode:
        print("❌ Email service is in mock mode - check RESEND_API_KEY")
        return False
    
    # Test sending an email
    print("\n5. Testing email send...")
    try:
        result = await email_service.send_stock_alert(
            symbol="TEST",
            current_price=100.0,
            previous_price=101.0,
            change_percent=-1.0,
            analysis="This is a test alert from the stock monitoring system.",
            key_factors=["Test factor 1", "Test factor 2"],
            alert_type="TEST"
        )
        
        print(f"✅ Email sent successfully!")
        print(f"   Subject: {result.subject}")
        print(f"   To: {result.to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Email send failed: {str(e)}")
        return False

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(test_resend_email())
    print(f"\n=== RESULT: {'SUCCESS' if success else 'FAILED'} ===")
