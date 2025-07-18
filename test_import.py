#!/usr/bin/env python3
"""
Test script to verify import functionality
"""

import requests
import json
import io

# Test CSV data with single row
test_csv = """asset_tag,manufacturer,model
TEST001,Samsung,Galaxy S21
"""

# Test configuration
base_url = "http://localhost:5000"
login_data = {
    "username": "admin",
    "password": "admin123"
}

def test_import():
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Login first
    login_response = session.post(f"{base_url}/login", data=login_data)
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        return
    
    print("Login successful")
    
    # Test import preview
    files = {'file': ('test.csv', io.StringIO(test_csv), 'text/csv')}
    preview_response = session.post(f"{base_url}/api/import/preview", files=files)
    
    if preview_response.status_code != 200:
        print(f"Preview failed: {preview_response.status_code}")
        print(f"Response: {preview_response.text}")
        return
    
    preview_data = preview_response.json()
    print(f"Preview successful: {preview_data}")
    
    # Test schema retrieval
    schema_response = session.post(f"{base_url}/api/import/schema", 
                                 json={"table_name": "phones"})
    
    if schema_response.status_code != 200:
        print(f"Schema failed: {schema_response.status_code}")
        print(f"Response: {schema_response.text}")
        return
    
    schema_data = schema_response.json()
    print(f"Schema successful: {schema_data}")
    
    # Test import process
    import_data = {
        "csv_data": test_csv,
        "target_table": "phones",
        "merge_key_csv": "asset_tag",
        "merge_key_db": "asset_tag",
        "column_mappings": {
            "asset_tag": "asset_tag",
            "manufacturer": "manufacturer",
            "model": "model"
        }
    }
    
    import_response = session.post(f"{base_url}/api/import/process", json=import_data)
    
    if import_response.status_code != 200:
        print(f"Import failed: {import_response.status_code}")
        print(f"Response: {import_response.text}")
        return
    
    import_result = import_response.json()
    print(f"Import successful: {import_result}")

if __name__ == "__main__":
    test_import()
