#!/usr/bin/env python3
"""
Debug script to test session management
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_session():
    """Test session management with login and API calls"""
    session = requests.Session()
    
    print("=== Session Management Debug Test ===")
    
    # Step 1: Login
    print("\n1. Testing login...")
    login_data = {
        'username': 'manager_north',
        'password': 'managerpass',
        'remember_me': 'on'
    }
    
    response = session.post(f"{BASE_URL}/login", data=login_data)
    print(f"Login response status: {response.status_code}")
    print(f"Login response headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print("✅ Login successful")
    else:
        print("❌ Login failed")
        return
    
    # Step 2: Test API call immediately
    print("\n2. Testing immediate API call...")
    api_response = session.get(f"{BASE_URL}/api/manager/team_status")
    print(f"API response status: {api_response.status_code}")
    
    if api_response.status_code == 200:
        print("✅ Immediate API call successful")
        print(f"Response length: {len(api_response.text)} characters")
    else:
        print("❌ Immediate API call failed")
        print(f"Response text: {api_response.text}")
    
    # Step 3: Test another API call
    print("\n3. Testing second API call...")
    api_response2 = session.get(f"{BASE_URL}/api/manager/selectable_phones")
    print(f"Second API response status: {api_response2.status_code}")
    
    if api_response2.status_code == 200:
        print("✅ Second API call successful")
    else:
        print("❌ Second API call failed")
        print(f"Response text: {api_response2.text}")
    
    # Step 4: Check session cookies
    print(f"\n4. Session cookies: {session.cookies}")

if __name__ == "__main__":
    try:
        test_session()
    except Exception as e:
        print(f"Test failed with error: {e}")
