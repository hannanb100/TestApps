#!/usr/bin/env python3
"""
Test SendPulse campaign email API
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

def test_sendpulse_campaign():
    print("=== Testing SendPulse Campaign Email API ===")
    
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
            
            # Try campaign email API
            email_url = "https://api.sendpulse.com/campaigns"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Try creating a simple campaign
            campaign_data = {
                "name": "Test Campaign",
                "subject": "Test Email",
                "html": "<p>Test email from SendPulse Campaign API</p>",
                "text": "Test email from SendPulse Campaign API",
                "sender_name": "Stock Alert System",
                "sender_email": "testingforben123@gmail.com",
                "from": {
                    "name": "Stock Alert System",
                    "email": "testingforben123@gmail.com"
                },
                "to": [
                    {
                        "name": "Ben",
                        "email": "testingforben123@gmail.com"
                    }
                ]
            }
            
            print("Trying campaign API...")
            campaign_response = requests.post(email_url, headers=headers, json=campaign_data)
            print(f"Campaign response status: {campaign_response.status_code}")
            print(f"Campaign response: {campaign_response.text}")
            
            if campaign_response.status_code == 200:
                print("✅ Campaign created successfully!")
            else:
                print("❌ Campaign creation failed")
                
        else:
            print("❌ Failed to get access token")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_sendpulse_campaign()
