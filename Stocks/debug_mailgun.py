#!/usr/bin/env python3
"""
Debug Mailgun credentials
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

def debug_mailgun():
    print("=== Debugging Mailgun Credentials ===")
    
    api_key = os.getenv('MAILGUN_API_KEY')
    domain = os.getenv('MAILGUN_DOMAIN')
    
    print(f"API Key: {api_key[:10]}..." if api_key else "None")
    print(f"Domain: {domain}")
    
    if not api_key or not domain:
        print("❌ Missing credentials")
        return
    
    # Test Mailgun API directly
    mailgun_url = f"https://api.mailgun.net/v3/{domain}/messages"
    
    print(f"Testing URL: {mailgun_url}")
    
    try:
        response = requests.post(
            mailgun_url,
            auth=("api", api_key),
            data={
                "from": f"Test <test@{domain}>",
                "to": ["testingforben123@gmail.com"],
                "subject": "Test Email",
                "text": "This is a test email"
            }
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 200:
            print("✅ Mailgun API working!")
        else:
            print("❌ Mailgun API error")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_mailgun()
