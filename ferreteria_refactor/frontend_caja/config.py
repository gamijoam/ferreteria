import os
from dotenv import load_dotenv

# Load .env explicitly from current directory or executable directory
load_dotenv()

API_BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
