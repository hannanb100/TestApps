#!/usr/bin/env python3
"""
Test OpenAI API directly
"""

import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

def test_openai_direct():
    print("=== Testing OpenAI API Directly ===")
    
    api_key = os.getenv('OPENAI_API_KEY')
    print(f"API Key found: {bool(api_key)}")
    print(f"API Key length: {len(api_key) if api_key else 0}")
    print(f"API Key starts with 'sk-': {api_key.startswith('sk-') if api_key else False}")
    
    if not api_key:
        print("❌ No API key found")
        return
    
    try:
        # Set the API key
        openai.api_key = api_key
        
        # Test a simple completion
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="Say hello",
            max_tokens=10
        )
        
        print(f"✅ OpenAI API working: {response.choices[0].text.strip()}")
        
    except Exception as e:
        print(f"❌ OpenAI API failed: {e}")

if __name__ == "__main__":
    test_openai_direct()
