#!/usr/bin/env python3
"""
Test the fixed OpenAI integration
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

from app.services.agent_service import AgentService

async def test_agent_service():
    print("=== Testing Fixed Agent Service ===")
    
    try:
        # Initialize the agent service
        agent = AgentService()
        print("✅ Agent service initialized successfully")
        
        # Test analysis
        analysis = await agent.analyze_stock_movement("WDAY", 250.0, 240.0)
        print(f"✅ Analysis generated: {analysis.analysis[:100]}...")
        print(f"   Confidence: {analysis.confidence_score}")
        print(f"   Key factors: {analysis.key_factors}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent_service())
