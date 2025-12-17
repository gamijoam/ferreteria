
import requests
import sys

URL = "http://127.0.0.1:8000/api/v1/token"
CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}

print(f"Testing Login at: {URL}")
try:
    response = requests.post(URL, data=CREDENTIALS)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Backend Login WORKS! The issue is in the Frontend.")
    else:
        print("❌ Backend returned error.")

except Exception as e:
    print(f"❌ Connection Failed: {e}")
