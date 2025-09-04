#!/usr/bin/env python3
"""
Test alert history service to see what's happening
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.alert_history_service import AlertHistoryService

def test_alert_history():
    print("=== Testing Alert History Service ===")
    
    # Initialize service
    service = AlertHistoryService()
    
    print(f"1. Storage file: {service.storage_file}")
    print(f"2. File exists: {os.path.exists(service.storage_file)}")
    print(f"3. Number of alerts in memory: {len(service.alerts)}")
    
    if os.path.exists(service.storage_file):
        print(f"4. File size: {os.path.getsize(service.storage_file)} bytes")
        
        # Read raw file content
        with open(service.storage_file, 'r') as f:
            raw_content = f.read()
            print(f"5. Raw file content: {raw_content[:500]}...")
    
    # Test get_recent_alerts
    print("6. Testing get_recent_alerts...")
    recent = service.get_recent_alerts(limit=10)
    print(f"   Recent alerts count: {len(recent)}")
    
    for i, alert in enumerate(recent):
        print(f"   Alert {i+1}: {alert.symbol} - {alert.change_percent:+.2f}% at {alert.timestamp}")

if __name__ == "__main__":
    test_alert_history()