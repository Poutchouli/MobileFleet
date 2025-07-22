import requests
import json

# Test the new team_by_sector endpoint
def test_team_by_sector():
    # First, log in to get a session
    login_data = {
        'username': 'manager_north',
        'password': 'manager123'
    }
    
    # Create a session
    session = requests.Session()
    
    # Login
    login_response = session.post('http://localhost:5000/login', data=login_data)
    print(f"Login Status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        # Test the new team_by_sector endpoint
        response = session.get('http://localhost:5000/api/manager/team_by_sector')
        print(f"Team by Sector Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Team by Sector Data:")
            print(json.dumps(data, indent=2, default=str))
        else:
            print(f"Error response: {response.text}")
    else:
        print(f"Login failed: {login_response.text}")

if __name__ == "__main__":
    test_team_by_sector()
