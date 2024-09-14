import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenRouter API key
OPENROUTER_API_KEY = "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" #os.getenv("OPENROUTER_API_KEY")

# OpenRouter authentication endpoint
AUTH_URL = "https://openrouter.ai/api/v1/auth/key"

def check_openrouter_limits():
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(AUTH_URL, headers=headers)
        response.raise_for_status()
        
        print("OpenRouter API Key Information:")
        print(response.text)
        
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        if response.text:
            print(f"Response content: {response.text}")

if __name__ == "__main__":
    if not OPENROUTER_API_KEY:
        print("Error: OPENROUTER_API_KEY is not set in the environment variables.")
    else:
        check_openrouter_limits()