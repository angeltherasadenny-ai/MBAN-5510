from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
print("Looking for .env at:", dotenv_path)

load_dotenv(dotenv_path=dotenv_path)

print("Google key loaded:", os.getenv("GOOGLE_MAPS_API_KEY") is not None)
print("Google key starts with:", (os.getenv("GOOGLE_MAPS_API_KEY") or "")[:6])
