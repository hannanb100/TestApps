#!/usr/bin/env python3
"""
Check SendPulse verified senders
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

def check_sendpulse_senders():
    print("=== Checking SendPulse Verified Senders ===")
    
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
            
            # Get verified senders
            senders_url = "https://api.sendpulse.com/smtp/senders"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            print("Getting verified senders...")
            senders_response = requests.get(senders_url, headers=headers)
            print(f"Senders response status: {senders_response.status_code}")
            print(f"Senders response: {senders_response.text}")
            
            if senders_response.status_code == 200:
                senders_data = senders_response.json()
                print("\n✅ Verified senders:")
                for sender in senders_data:
                    print(f"  - {sender}")
            else:
                print("❌ Failed to get senders")
                
        else:
            print("❌ Failed to get access token")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_sendpulse_senders()
