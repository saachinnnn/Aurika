import os
import json
import time
import requests
import questionary
from pathlib import Path
from dotenv import load_dotenv
from collections import defaultdict
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.theme import Theme
from rich.text import Text
from rich import print as rprint

# -----------------------------------------------------------------------------
# Configuration & Setup
# -----------------------------------------------------------------------------

# Custom Rich Theme
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "highlight": "magenta",
})
console = Console(theme=custom_theme)

# Load .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

GRAPHQL_URL = "https://leetcode.com/graphql/"
DATA_DIR = Path("data")

# Fields to strictly EXCLUDE from the saved JSON
EXCLUDED_FIELDS = {
    # Judge / Execution Noise
    "testBodies", "testDescriptions", "testInfo", 
    "fullCodeOutput", "stdOutput", "codeOutput", 
    "lastTestcase", "expectedOutput", 
    "totalCorrect", "totalTestcases", 
    "runtimeDistribution", "memoryDistribution",
    # Frontend / UI / Tracking
    "userAvatar", "avatar", "profileUrl",
    # Other
    "codeSnippets"
}

# -----------------------------------------------------------------------------
# GraphQL Queries
# -----------------------------------------------------------------------------

QUERY_USER_STATUS = """
query globalData {
    userStatus {
        username
        isSignedIn
    }
}
"""

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

QUERY_SUBMISSION_DETAILS = """
query submissionDetails($submissionId: Int!) {
    submissionDetails(submissionId: $submissionId) {
        runtime
        runtimeDisplay
        runtimePercentile
        # runtimeDistribution (Dropped later)
        memory
        memoryDisplay
        memoryPercentile
        # memoryDistribution (Dropped later)
        code
        timestamp
        statusCode
        user {
            username
            profile {
                realName
                # userAvatar (Dropped later)
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
        # Judge noise (Dropped later)
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

def clean_data(data):
    """
    Recursively remove excluded keys from a dictionary or list.
    """
    if isinstance(data, dict):
        return {
            k: clean_data(v) 
            for k, v in data.items() 
            if k not in EXCLUDED_FIELDS
        }
    elif isinstance(data, list):
        return [clean_data(item) for item in data]
    else:
        return data

def get_headers(session, csrf, clearance):
    return {
        "Content-Type": "application/json",
        "Referer": "https://leetcode.com/",
        "Origin": "https://leetcode.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-CSRFToken": csrf,
        "Cookie": f"LEETCODE_SESSION={session}; csrftoken={csrf}; cf_clearance={clearance}",
    }

def gql_request(query, variables, operation_name, headers):
    payload = {
        "query": query,
        "variables": variables or {}
    }
    if operation_name:
        payload["operationName"] = operation_name
        
    try:
        response = requests.post(GRAPHQL_URL, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        console.print(f"[error]Request failed: {e}[/error]")
        if 'response' in locals() and hasattr(response, 'text'):
            console.print(response.text)
        return None

def get_username(headers):
    with console.status("[bold cyan]Authenticating...", spinner="dots"):
        data = gql_request(QUERY_USER_STATUS, {}, "globalData", headers)
        if not data or "data" not in data or not data["data"]["userStatus"]["isSignedIn"]:
            console.print("[error]Auth Failed: User is not signed in. Check credentials.[/error]")
            return None
    return data["data"]["userStatus"]["username"]

def fetch_all_submissions_list(headers):
    offset = 0
    limit = 20
    all_submissions = []
    
    with console.status("[bold cyan]Fetching submission history...", spinner="dots") as status:
        while True:
            data = gql_request(QUERY_SUBMISSION_LIST, {"offset": offset, "limit": limit}, "submissionList", headers)
            if not data or "data" not in data or not data["data"]["submissionList"]:
                console.print("[warning]Failed to fetch submission list or end reached unexpectedly.[/warning]")
                break
                
            sub_list = data["data"]["submissionList"]
            submissions = sub_list["submissions"]
            has_next = sub_list["hasNext"]
            
            all_submissions.extend(submissions)
            status.update(f"[bold cyan]Fetching submission history... (Fetched {len(all_submissions)} items)")
            
            if not has_next:
                break
                
            offset += limit
            time.sleep(0.5)
        
    return all_submissions

def run_extraction(session, csrf, clearance):
    headers = get_headers(session, csrf, clearance)
    
    # 1. Get Username
    username = get_username(headers)
    if not username:
        return
    
    console.print(f"[success]Authenticated as: [bold]{username}[/bold][/success]")
    
    user_dir = DATA_DIR / username
    user_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Fetch All Submissions List
    submissions_summary = fetch_all_submissions_list(headers)
    console.print(f"[info]Total Submissions Found: [bold]{len(submissions_summary)}[/bold][/info]")
    
    # 3. Group by Question
    grouped = defaultdict(list)
    for sub in submissions_summary:
        slug = sub.get("titleSlug")
        if slug:
            grouped[slug].append(sub)
            
    console.print(f"[info]Unique Problems Attempted: [bold]{len(grouped)}[/bold][/info]")
    
    # 4. Process Each Question
    console.print("\n[bold]Starting detailed extraction...[/bold]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        
        main_task = progress.add_task("[cyan]Processing Problems...", total=len(grouped))
        
        for i, (slug, subs) in enumerate(grouped.items(), 1):
            progress.update(main_task, description=f"[cyan]Processing: {slug}")
            
            # A. Fetch Problem Metadata
            meta_data = gql_request(QUERY_PROBLEM_DETAILS, {"titleSlug": slug}, "selectProblem", headers)
            if not meta_data or "data" not in meta_data:
                console.print(f"[warning]Failed to get metadata for {slug}[/warning]")
                question_data = {"error": "Failed to fetch"}
            else:
                question_data = clean_data(meta_data["data"]["question"])
                
            # B. Fetch Submission Code
            full_submissions = []
            for sub in subs:
                sub_id = sub["id"]
                detail_data = gql_request(QUERY_SUBMISSION_DETAILS, {"submissionId": sub_id}, "submissionDetails", headers)
                
                if detail_data and "data" in detail_data and detail_data["data"]["submissionDetails"]:
                    # Merge and Clean
                    cleaned_details = clean_data(detail_data["data"]["submissionDetails"])
                    full_sub = {**sub, **cleaned_details}
                    full_submissions.append(full_sub)
                else:
                    console.print(f"[warning]Failed to fetch details for {sub_id}[/warning]")
                    full_submissions.append(sub)
                
                time.sleep(0.3)
                
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
                
            progress.advance(main_task)
            time.sleep(0.5)

    console.print(Panel(f"[bold green]Extraction Complete![/bold green]\nData saved to: {user_dir}", title="Success", border_style="green"))

def interactive_cli():
    console.print(Panel.fit(
        "[bold cyan]LeetCode Data Extractor[/bold cyan]\n"
        "Extract your submissions, code, and problem metadata.",
        border_style="cyan"
    ))
    
    # Check env first
    env_session = os.getenv("LEETCODE_SESSION")
    env_csrf = os.getenv("LEETCODE_CSRF_TOKEN")
    env_cf = os.getenv("CF_CLEARANCE")
    
    use_env = False
    if env_session and env_csrf and env_cf:
        use_env = questionary.confirm(
            "Found credentials in .env file. Do you want to use them?",
            default=True
        ).ask()
            
    if use_env:
        session = env_session
        csrf = env_csrf
        cf = env_cf
    else:
        console.print("\n[bold]Please enter your LeetCode credentials:[/bold]")
        console.print("[dim](You can find these in your browser cookies/headers)[/dim]")
        
        session = questionary.password("LEETCODE_SESSION:").ask()
        csrf = questionary.text("csrftoken:").ask()
        cf = questionary.text("cf_clearance:").ask()
        
        if not session or not csrf or not cf:
            console.print("[error]All credentials are required![/error]")
            return

        # Optionally save to .env
        save = questionary.confirm(
            "Save these to .env for future use?",
            default=True
        ).ask()
        
        if save:
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(f"LEETCODE_SESSION={session}\n")
                f.write(f"LEETCODE_CSRF_TOKEN={csrf}\n")
                f.write(f"CF_CLEARANCE={cf}\n")
            console.print("[success]Saved to .env[/success]")

    console.print() # Spacer
    run_extraction(session, csrf, cf)

if __name__ == "__main__":
    interactive_cli()
