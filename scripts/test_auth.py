import os
import requests
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
CSRF_TOKEN = os.getenv("LEETCODE_CSRF_TOKEN")

HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com/",
    "X-CSRFToken": CSRF_TOKEN,
    "Cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}; csrftoken={CSRF_TOKEN}",
}

GRAPHQL_URL = "https://leetcode.com/graphql/"

query = {
    "query": """
    query globalData {
        userStatus {
            userId
            username
            isSignedIn
            isPremium
        }
    }
    """
}

response = requests.post(GRAPHQL_URL, headers=HEADERS, json=query)
print(response.text)
