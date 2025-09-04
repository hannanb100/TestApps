#!/usr/bin/env python3
"""
Test OpenAI API key on Railway
"""

import requests
import json

def test_openai_railway():
    print("=== Testing OpenAI API on Railway ===")
    
    # Test the health endpoint first
    try:
        response = requests.get("https://testapps-production-665f.up.railway.app/health")
        print(f"Health check: {response.status_code}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Test a simple API endpoint that might use OpenAI
    try:
        response = requests.get("https://testapps-production-665f.up.railway.app/api/v1/stocks/WDAY/quote")
        print(f"Stock quote: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"WDAY price: ${data.get('price', 'N/A')}")
    except Exception as e:
        print(f"Stock quote failed: {e}")

if __name__ == "__main__":
    test_openai_railway()
