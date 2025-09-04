#!/usr/bin/env python3
"""
Test SendPulse REST API directly
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

def test_sendpulse_rest():
    print("=== Testing SendPulse REST API ===")
    
    user_id = os.getenv('SENDPULSE_USER_ID')
    secret = os.getenv('SENDPULSE_SECRET')
    
    print(f"User ID: {user_id}")
    print(f"Secret: {secret[:10]}..." if secret else "None")
    
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
    
    print("Getting access token...")
    try:
        token_response = requests.post(token_url, data=token_data)
        print(f"Token response status: {token_response.status_code}")
        print(f"Token response: {token_response.text}")
        
        if token_response.status_code == 200:
            token_data = token_response.json()
            access_token = token_data.get('access_token')
            print(f"Access token: {access_token[:20]}..." if access_token else "None")
            
            if access_token:
                # Try to send email using REST API
                email_url = "https://api.sendpulse.com/smtp/emails"
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                email_data = {
                    "email": {
                        "subject": "Test Email",
                        "html": "<p>Test email from SendPulse REST API</p>",
                        "text": "Test email from SendPulse REST API",
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
                }
                
                print("Sending email via REST API...")
                email_response = requests.post(email_url, headers=headers, json=email_data)
                print(f"Email response status: {email_response.status_code}")
                print(f"Email response: {email_response.text}")
                
                if email_response.status_code == 200:
                    print("✅ Email sent successfully!")
                else:
                    print("❌ Email send failed")
            else:
                print("❌ No access token received")
        else:
            print("❌ Failed to get access token")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_sendpulse_rest()
