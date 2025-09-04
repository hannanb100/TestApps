#!/usr/bin/env python3
"""
Test SendPulse email service locally
"""

import sys
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.email_service import EmailService

async def test_sendpulse():
    print("=== Testing SendPulse Email Service ===")
    
    # Initialize email service
    email_service = EmailService()
    
    print(f"1. Mock mode: {email_service.is_mock_mode}")
    print(f"2. From email: {email_service.from_email}")
    print(f"3. To email: {email_service.to_email}")
    print(f"4. SendPulse User ID set: {bool(email_service.sendpulse_user_id)}")
    print(f"5. SendPulse Secret set: {bool(email_service.sendpulse_secret)}")
    
    if email_service.is_mock_mode:
        print("❌ Email service is in mock mode - check SENDPULSE_USER_ID and SENDPULSE_SECRET")
        return False
    
    # Prepare test email
    to_email = email_service.to_email
    subject = f"Test SendPulse Email - {datetime.utcnow().isoformat()}"
    html_content = "<p>This is a <strong>test email</strong> sent via SendPulse.</p>"
    text_content = "This is a test email sent via SendPulse."
    
    print(f"6. Sending test email to {to_email}...")
    try:
        await email_service.send_email(to_email, subject, html_content, text_content)
        print("✅ Test email sent successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")
        return False

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(test_sendpulse())
    print(f"\n=== RESULT: {'SUCCESS' if result else 'FAILED'} ===")
