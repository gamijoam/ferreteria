import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_session_persistence():
    # 1. Login
    print("Logging in as temp_admin...")
    login_data = {"username": "temp_admin", "password": "temp123"}
    try:
        resp = requests.post(f"{BASE_URL}/auth/token", data=login_data)
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} - {resp.text}")
            return
        
        token = resp.json()["access_token"]
        print("Login successful. Token obtained.")
        
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Check Current Session
        print("\nChecking Current Session (GET /cash/sessions/current)...")
        resp = requests.get(f"{BASE_URL}/cash/sessions/current", headers=headers)
        
        if resp.status_code == 200:
            print("Session active according to GET:")
            print(json.dumps(resp.json(), indent=2))
        elif resp.status_code == 404:
            print("GET returned 404: No active session found.")
            
            # 3. Try to Open Session (to see if backend thinks it's open)
            print("\nAttempting to Open Session (POST /cash/sessions/open)...")
            open_data = {
                "initial_cash": 100,
                "initial_cash_bs": 0,
                "currencies": []
            }
            resp = requests.post(f"{BASE_URL}/cash/sessions/open", json=open_data, headers=headers)
            
            if resp.status_code == 200:
                print("Session opened successfully (it was indeed closed).")
            elif resp.status_code == 400:
                print("POST returned 400:", resp.json())
                print("BUG CONFIRMED: Backend says 'Already Open' but GET returned 404!")
            else:
                print(f"Unexpected POST response: {resp.status_code} - {resp.text}")

        else:
            print(f"Unexpected GET response: {resp.status_code} - {resp.text}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    test_session_persistence()
