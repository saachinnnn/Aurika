import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
from collections import defaultdict

# -----------------------------------------------------------------------------
# Configuration & Setup
# -----------------------------------------------------------------------------

# Load .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
CSRF_TOKEN = os.getenv("LEETCODE_CSRF_TOKEN")
CF_CLEARANCE = os.getenv("CF_CLEARANCE")

if not LEETCODE_SESSION or not CSRF_TOKEN:
    print("❌ Error: Missing LEETCODE_SESSION or CSRF_TOKEN in .env")
    exit(1)

HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com/",
    "Origin": "https://leetcode.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-CSRFToken": CSRF_TOKEN,
    "Cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}; csrftoken={CSRF_TOKEN}; cf_clearance={CF_CLEARANCE}",
}

GRAPHQL_URL = "https://leetcode.com/graphql/"
DATA_DIR = Path("data")

# -----------------------------------------------------------------------------
# GraphQL Queries
# -----------------------------------------------------------------------------

# Query 1: Get User Status (to find username)
QUERY_USER_STATUS = """
query globalData {
    userStatus {
        username
        isSignedIn
    }
}
"""

# Query 2: Submission List (History)
# Using generic submissionList. If this fails, we might fall back to recentSubmissionList 
# but that's limited. We assume submissionList works with valid Auth.
QUERY_SUBMISSION_LIST = """
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
"""

# Query 3: Submission Details (Code)
QUERY_SUBMISSION_DETAILS = """
query submissionDetails($submissionId: Int!) {
    submissionDetails(submissionId: $submissionId) {
        runtime
        runtimeDisplay
        runtimePercentile
        runtimeDistribution
        memory
        memoryDisplay
        memoryPercentile
        memoryDistribution
        code
        timestamp
        statusCode
        user {
            username
            profile {
                realName
                userAvatar
            }
        }
        lang {
            name
            verboseName
        }
        question {
            questionId
            titleSlug
            hasFrontendPreview
        }
        notes
        flagType
        topicTags {
            tagId
            slug
            name
        }
        runtimeError
        compileError
        lastTestcase
        codeOutput
        expectedOutput
        totalCorrect
        totalTestcases
        fullCodeOutput
        testDescriptions
        testBodies
        testInfo
        stdOutput
    }
}
"""

# Query 4: Problem Metadata (Content, Tags, Difficulty)
QUERY_PROBLEM_DETAILS = """
query selectProblem($titleSlug: String!) {
    question(titleSlug: $titleSlug) {
        questionId
        title
        titleSlug
        content
        difficulty
        stats
        topicTags {
            name
            slug
            translatedName
        }
        hints
        codeSnippets {
            lang
            langSlug
            code
        }
    }
}
"""

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def gql_request(query, variables=None, operation_name=None):
    payload = {
        "query": query,
        "variables": variables or {}
    }
    if operation_name:
        payload["operationName"] = operation_name
        
    try:
        response = requests.post(GRAPHQL_URL, headers=HEADERS, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Request failed: {e}")
        if hasattr(response, 'text'):
            print(response.text)
        return None

def get_username():
    print("Fetching user profile...")
    data = gql_request(QUERY_USER_STATUS, operation_name="globalData")
    if not data or "data" not in data or not data["data"]["userStatus"]["isSignedIn"]:
        print("Auth Failed: User is not signed in. Check cookies.")
        return None
    return data["data"]["userStatus"]["username"]

def fetch_all_submissions_list():
    """
    Fetches the metadata of ALL submissions (pagination).
    Returns a list of submission summaries.
    """
    offset = 0
    limit = 20
    all_submissions = []
    
    print("Fetching submission list...")
    while True:
        data = gql_request(QUERY_SUBMISSION_LIST, {"offset": offset, "limit": limit}, "submissionList")
        if not data or "data" not in data or not data["data"]["submissionList"]:
            print("Failed to fetch submission list or end reached unexpectedly.")
            break
            
        sub_list = data["data"]["submissionList"]
        submissions = sub_list["submissions"]
        has_next = sub_list["hasNext"]
        
        all_submissions.extend(submissions)
        print(f"   Fetched {len(submissions)} items (Offset: {offset})")
        
        if not has_next:
            break
            
        offset += limit
        time.sleep(1) # Rate limit politeness
        
    return all_submissions

def process_pipeline():
    # 1. Get Username
    username = get_username()
    if not username:
        return
    
    print(f"Authenticated as: {username}")
    
    user_dir = DATA_DIR / username
    user_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Fetch All Submissions List
    submissions_summary = fetch_all_submissions_list()
    print(f"Total Submissions Found: {len(submissions_summary)}")
    
    # 3. Group by Question (titleSlug)
    grouped = defaultdict(list)
    for sub in submissions_summary:
        slug = sub.get("titleSlug")
        if slug:
            grouped[slug].append(sub)
            
    print(f"Unique Problems Attempted: {len(grouped)}")
    
    # 4. Process Each Question
    for i, (slug, subs) in enumerate(grouped.items(), 1):
        print(f"[{i}/{len(grouped)}] Processing: {slug}")
        
        # Check if file exists (optional: skip if already done?)
        # For now, we overwrite to ensure "perfect sync" and missing data is added
        
        # A. Fetch Problem Metadata (ONCE per question)
        print(f"   Getting metadata for {slug}...")
        meta_data = gql_request(QUERY_PROBLEM_DETAILS, {"titleSlug": slug}, "selectProblem")
        if not meta_data or "data" not in meta_data:
            print(f"   Failed to get metadata for {slug}")
            question_data = {"error": "Failed to fetch"}
        else:
            question_data = meta_data["data"]["question"]
            
        # B. Fetch Submission Code for EACH submission
        full_submissions = []
        for sub in subs:
            sub_id = sub["id"]
            # Optimization: If we have cached details in raw/submission_details, use that?
            # User wants "ideal pipeline", let's fetch fresh or reuse if we want to be fast.
            # To be safe and "Extremely crucial", let's fetch fresh or check cache.
            # Given the constraints, let's fetch to be sure we get everything.
            
            print(f"   Fetching code for submission {sub_id}...")
            detail_data = gql_request(QUERY_SUBMISSION_DETAILS, {"submissionId": sub_id}, "submissionDetails")
            
            if detail_data and "data" in detail_data and detail_data["data"]["submissionDetails"]:
                # Merge summary info with detailed info
                full_sub = {**sub, **detail_data["data"]["submissionDetails"]}
                full_submissions.append(full_sub)
            else:
                print(f"   Failed to fetch details for {sub_id}")
                full_submissions.append(sub) # Keep summary at least
            
            time.sleep(0.5) # Sleep between submissions
            
        # 5. Construct Final JSON
        final_output = {
            "question_name": slug,
            "problem_metadata": question_data,
            "submissions": full_submissions
        }
        
        # 6. Save
        file_path = user_dir / f"{slug}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(final_output, f, indent=2, ensure_ascii=False)
            
        print(f"   Saved to {file_path}")
        time.sleep(1) # Sleep between questions

if __name__ == "__main__":
    process_pipeline()
