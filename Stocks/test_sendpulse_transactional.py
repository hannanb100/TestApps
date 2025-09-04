#!/usr/bin/env python3
"""
Test SendPulse transactional email API
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

def test_sendpulse_transactional():
    print("=== Testing SendPulse Transactional Email API ===")
    
    user_id = os.getenv('SENDPULSE_USER_ID')
    secret = os.getenv('SENDPULSE_SECRET')
    
    if not user_id or not secret:
        print("❌ Missing credentials")
        return
    
    # Get access token
    token_url = "https://api.sendpulse.com/oauth/access_token"
    token_data = {
        "grant_type": "client_credentials",
        "client_id": user_id,
        "client_secret": secret
    }
    
    try:
        token_response = requests.post(token_url, data=token_data)
        if token_response.status_code == 200:
            token_data = token_response.json()
            access_token = token_data.get('access_token')
            
            # Try transactional email API (different endpoint)
            email_url = "https://api.sendpulse.com/transactional/emails"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Try different email formats
            email_formats = [
                # Format 1: Basic transactional
                {
                    "subject": "Test Email",
                    "html": "<p>Test email from SendPulse Transactional API</p>",
                    "text": "Test email from SendPulse Transactional API",
                    "from": "testingforben123@gmail.com",
                    "to": "testingforben123@gmail.com"
                },
                # Format 2: With name
                {
                    "subject": "Test Email",
                    "html": "<p>Test email from SendPulse Transactional API</p>",
                    "text": "Test email from SendPulse Transactional API",
                    "from": {
                        "name": "Stock Alert System",
                        "email": "testingforben123@gmail.com"
                    },
                    "to": {
                        "name": "Ben",
                        "email": "testingforben123@gmail.com"
                    }
                }
            ]
            
            for i, email_data in enumerate(email_formats, 1):
                print(f"\nTrying transactional format {i}...")
                email_response = requests.post(email_url, headers=headers, json=email_data)
                print(f"Email response status: {email_response.status_code}")
                print(f"Email response: {email_response.text}")
                
                if email_response.status_code == 200:
                    print("✅ Email sent successfully!")
                    break
                else:
                    print("❌ Email send failed")
                    
        else:
            print("❌ Failed to get access token")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_sendpulse_transactional()
