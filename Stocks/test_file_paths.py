#!/usr/bin/env python3
"""
Test file paths and working directory
"""

import os
import sys

print("=== File Path Test ===")
print(f"1. Current working directory: {os.getcwd()}")
print(f"2. Script directory: {os.path.dirname(os.path.abspath(__file__))}")
print(f"3. Files in current directory: {os.listdir('.')}")
print(f"4. alert_history.json exists: {os.path.exists('alert_history.json')}")
print(f"5. alert_history.json absolute path: {os.path.abspath('alert_history.json')}")

# Check if there are any JSON files
json_files = [f for f in os.listdir('.') if f.endswith('.json')]
print(f"6. JSON files in current directory: {json_files}")

# Check if there are any alert_history files
alert_files = [f for f in os.listdir('.') if 'alert' in f.lower()]
print(f"7. Alert-related files: {alert_files}")
