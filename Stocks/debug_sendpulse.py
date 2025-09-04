#!/usr/bin/env python3
"""
Debug SendPulse API call
"""

import os
from dotenv import load_dotenv
from pysendpulse.pysendpulse import PySendPulse

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

def debug_sendpulse():
    print("=== Debugging SendPulse API ===")
    
    user_id = os.getenv('SENDPULSE_USER_ID')
    secret = os.getenv('SENDPULSE_SECRET')
    
    print(f"User ID: {user_id}")
    print(f"Secret: {secret[:10]}..." if secret else "None")
    
    if not user_id or not secret:
        print("❌ Missing credentials")
        return
    
    try:
        # Initialize SendPulse
        sp = PySendPulse(user_id, secret, 'file')
        print("✅ SendPulse initialized")
        
        # Try a simple email with different format
        print("Trying simple email...")
        
        # Try different email formats
        formats_to_try = [
            # Format 1: Basic
            {
                'subject': 'Test Email',
                'html': '<p>Test</p>',
                'text': 'Test',
                'from': {
                    'name': 'Test',
                    'email': 'testingforben123@gmail.com'
                },
                'to': [
                    {
                        'name': 'Ben',
                        'email': 'testingforben123@gmail.com'
                    }
                ]
            },
            # Format 2: Different structure
            {
                'subject': 'Test Email',
                'html': '<p>Test</p>',
                'text': 'Test',
                'from': 'testingforben123@gmail.com',
                'to': 'testingforben123@gmail.com'
            }
        ]
        
        # Try different SendPulse methods
        email_format = formats_to_try[0]  # Use the first format
        methods_to_try = [
            ('smtp_send_mail', email_format),
            ('send_mail', email_format),
            ('send_email', email_format)
        ]
        
        for method_name, email_format in methods_to_try:
            print(f"\nTrying method: {method_name}")
            try:
                if hasattr(sp, method_name):
                    method = getattr(sp, method_name)
                    result = method(email_format)
                    print(f"Result: {result}")
                    
                    if result and 'data' in result and result['data'].get('is_error'):
                        print(f"Error details: {result['data']}")
                        # Try to get more detailed error info
                        if 'message' in result['data']:
                            print(f"Error message: {result['data']['message']}")
                        if 'errors' in result['data']:
                            print(f"Validation errors: {result['data']['errors']}")
                    else:
                        print("✅ This method worked!")
                        break
                else:
                    print(f"Method {method_name} not found")
            except Exception as e:
                print(f"Error with {method_name}: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_sendpulse()
