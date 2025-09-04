#!/usr/bin/env python3
"""
Test SendPulse using official repository format
"""

import os
from dotenv import load_dotenv
from pysendpulse.pysendpulse import PySendPulse

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

def test_sendpulse_official():
    print("=== Testing SendPulse with Official Format ===")
    
    user_id = os.getenv('SENDPULSE_USER_ID')
    secret = os.getenv('SENDPULSE_SECRET')
    
    if not user_id or not secret:
        print("❌ Missing credentials")
        return
    
    try:
        # Initialize SendPulse exactly as shown in official repo
        SPApiProxy = PySendPulse(user_id, secret, 'file')
        print("✅ SendPulse initialized")
        
        # Use the exact format from the official repository
        email = {
            'subject': 'Test Email',
            'from': {
                'name': 'Stock Alert System',
                'email': 'testingforben123@gmail.com',
            },
            'to': [
                {
                    'name': 'Ben',
                    'email': 'testingforben123@gmail.com',
                }
            ],
            'html': '<p>This is a test email from SendPulse.</p>',
            'text': 'This is a test email from SendPulse.',
        }
        
        print("Sending email with official format...")
        result = SPApiProxy.smtp_send_mail(email)
        print(f"Result: {result}")
        
        if result and result.get('result'):
            print("✅ Email sent successfully!")
        else:
            print("❌ Email send failed")
            if result and 'data' in result:
                print(f"Error details: {result['data']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_sendpulse_official()
