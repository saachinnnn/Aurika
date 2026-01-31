import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

# Explicitly load .env from the project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
CSRF_TOKEN = os.getenv("LEETCODE_CSRF_TOKEN")
CF_CLEARANCE = os.getenv("CF_CLEARANCE")

if not LEETCODE_SESSION or not CSRF_TOKEN:
    raise Exception("Missing LEETCODE_SESSION or CSRF token")

HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com/",
    "Origin": "https://leetcode.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-CSRFToken": CSRF_TOKEN,
    "Cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}; csrftoken={CSRF_TOKEN}; cf_clearance={CF_CLEARANCE}",
}

GRAPHQL_URL = "https://leetcode.com/graphql/"

RAW_LIST_DIR = Path("data/raw/submissions_list")
RAW_DETAILS_DIR = Path("data/raw/submission_details")

RAW_LIST_DIR.mkdir(parents=True, exist_ok=True)
RAW_DETAILS_DIR.mkdir(parents=True, exist_ok=True)


def fetch_submission_list(offset=0, limit=20):
    query = {
        "operationName": "submissionList",
        "variables": {"offset": offset, "limit": limit},
        "query": """
        query submissionList($offset: Int!, $limit: Int!) {
            submissionList(offset: $offset, limit: $limit) {
                hasNext
                submissions {
                    id
                    statusDisplay
                    lang
                    runtime
                    memory
                    timestamp
                    title
                    titleSlug
                }
            }
        }
        """,
    }
    response = requests.post(GRAPHQL_URL, headers=HEADERS, json=query)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error response: {response.text}")
        raise e
    return response.json()


def fetch_submission_details(submission_id):
    query = {
        "operationName": "submissionDetails",
        "variables": {"submissionId": submission_id},
        "query": """
        query submissionDetails($submissionId: Int!) {
            submissionDetails(submissionId: $submissionId) {
                code
                runtime
                memory
                timestamp
                statusCode
                lang {
                    name
                    verboseName
                }
                question {
                    questionId
                    titleSlug
                }
            }
        }
        """,
    }
    response = requests.post(GRAPHQL_URL, headers=HEADERS, json=query)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error response: {response.text}")
        raise e
    return response.json()


def main():
    offset = 0
    limit = 20

    while True:
        print(f"Fetching submissions offset {offset}")
        data = fetch_submission_list(offset, limit)
        
        if "errors" in data:
            print(f"GraphQL Errors: {data['errors']}")
            break
            
        node = data["data"]["submissionList"]
        submissions = node["submissions"]
        has_next = node["hasNext"]

        if not submissions:
            print("Done (no more submissions).")
            print(f"Debug: Full response data: {data}")
            break

        with open(RAW_LIST_DIR / f"list_{offset}.json", "w") as f:
            json.dump(data, f, indent=2)

        for sub in submissions:
            sub_id = sub["id"]
            # Skip if already downloaded (optional optimization)
            if (RAW_DETAILS_DIR / f"{sub_id}.json").exists():
                 continue

            print(f"Fetching submission {sub_id}")
            try:
                detail = fetch_submission_details(sub_id)
                with open(RAW_DETAILS_DIR / f"{sub_id}.json", "w") as f:
                    json.dump(detail, f, indent=2)
            except Exception as e:
                print(f"Failed to fetch details for {sub_id}: {e}")

            time.sleep(1.2)

        if not has_next:
            print("Done (hasNext is False).")
            break

        offset += limit
        time.sleep(2)


if __name__ == "__main__":
    main()
