import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

# Explicitly load .env from the project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
CSRF_TOKEN = os.getenv("LEETCODE_CSRF_TOKEN")
CF_CLEARANCE = os.getenv("CF_CLEARANCE")

HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com/",
    "Origin": "https://leetcode.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-CSRFToken": CSRF_TOKEN,
    "Cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}; csrftoken={CSRF_TOKEN}; cf_clearance={CF_CLEARANCE}",
}

GRAPHQL_URL = "https://leetcode.com/graphql/"

def main():
    query = {
        "operationName": "getRecentSubmissions",
        "variables": {"username": "hpmso99", "limit": 20},
        "query": """
        query getRecentSubmissions($username: String!, $limit: Int) {
            recentSubmissionList(username: $username, limit: $limit) {
                title
                titleSlug
                timestamp
                statusDisplay
                lang
            }
        }
        """
    }
    
    print("Fetching recent submissions...")
    response = requests.post(GRAPHQL_URL, headers=HEADERS, json=query)
    try:
        response.raise_for_status()
        print(response.json())
    except Exception as e:
        print(f"Error: {e}")
        print(response.text)

if __name__ == "__main__":
    main()