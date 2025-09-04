#!/usr/bin/env python3
"""
Simple Resend API test
"""

import os
from dotenv import load_dotenv
import resend

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

def test_resend_simple():
    print("=== Simple Resend Test ===")
    
    api_key = os.getenv('RESEND_API_KEY')
    print(f"API Key found: {bool(api_key)}")
    print(f"API Key starts with 're_': {api_key.startswith('re_') if api_key else False}")
    
    if not api_key:
        print("❌ No API key found")
        return False
    
    # Set the API key
    resend.api_key = api_key
    
    try:
        # Send a simple test email
        response = resend.Emails.send({
            "from": "testingforben123@gmail.com",
            "to": ["testingforben123@gmail.com"],
            "subject": "Test Email from Stock Alerts",
            "html": "<h1>Test Email</h1><p>This is a test email from the stock alert system.</p>",
        })
        
        print(f"✅ Email sent successfully!")
        print(f"Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Email send failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_resend_simple()
    print(f"\n=== RESULT: {'SUCCESS' if success else 'FAILED'} ===")
