#!/usr/bin/env python3
"""
Debug Resend API issues
"""

import os
from dotenv import load_dotenv
import resend
import json

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

def test_resend_debug():
    print("=== Resend Debug Test ===")
    
    api_key = os.getenv('RESEND_API_KEY')
    print(f"API Key found: {bool(api_key)}")
    print(f"API Key length: {len(api_key) if api_key else 0}")
    print(f"API Key starts with 're_': {api_key.startswith('re_') if api_key else False}")
    
    if not api_key:
        print("❌ No API key found")
        return False
    
    # Set the API key
    resend.api_key = api_key
    
    try:
        # Try to send a simple test email using Resend test addresses
        print("Attempting to send test email...")
        response = resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": ["delivered@resend.dev"],
            "subject": "Test Email from Stock Alerts",
            "html": "<h1>Test Email</h1><p>This is a test email from the stock alert system.</p>",
        })
        
        print(f"✅ Email sent successfully!")
        print(f"Response type: {type(response)}")
        print(f"Response: {response}")
        
        if hasattr(response, '__dict__'):
            print(f"Response attributes: {response.__dict__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Email send failed: {str(e)}")
        print(f"Error type: {type(e)}")
        
        # Try to get more details about the error
        if hasattr(e, 'response'):
            print(f"Response status: {e.response.status_code if hasattr(e.response, 'status_code') else 'Unknown'}")
            print(f"Response text: {e.response.text if hasattr(e.response, 'text') else 'Unknown'}")
        
        return False

if __name__ == "__main__":
    success = test_resend_debug()
    print(f"\n=== RESULT: {'SUCCESS' if success else 'FAILED'} ===")
