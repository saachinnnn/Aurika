import json
import time
import logging
import httpx
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Any, Optional
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.console import Console

from src.pipeline.config import GRAPHQL_URL, RAW_DATA_DIR
from src.pipeline.stage_1_harvester.authentication import AuthenticationError

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Constants & Queries
# -----------------------------------------------------------------------------

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
# Harvester Logic
# -----------------------------------------------------------------------------

class LeetCodeHarvester:
    def __init__(self, client: httpx.Client, username: str, console: Optional[Console] = None):
        self.client = client
        self.username = username
        self.console = console or Console()
        self.user_raw_dir = RAW_DATA_DIR / username
        self.user_raw_dir.mkdir(parents=True, exist_ok=True)

    def _clean_data(self, data: Any) -> Any:
        """Recursively remove excluded keys."""
        if isinstance(data, dict):
            return {
                k: self._clean_data(v) 
                for k, v in data.items() 
                if k not in EXCLUDED_FIELDS
            }
        elif isinstance(data, list):
            return [self._clean_data(item) for item in data]
        else:
            return data

    def _gql_request(self, query: str, variables: dict, operation_name: str) -> Optional[dict]:
        try:
            response = self.client.post(
                GRAPHQL_URL,
                json={"query": query, "variables": variables, "operationName": operation_name}
            )
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                logger.error(f"GraphQL Error in {operation_name}: {data['errors']}")
                if self.console:
                    self.console.print(f"[bold red]GraphQL Error:[/bold red] {data['errors']}")
                return None
                
            return data
        except httpx.HTTPError as e:
            logger.error(f"Request failed for {operation_name}: {e}")
            if self.console:
                self.console.print(f"[bold red]Request Failed:[/bold red] {e}")
            return None

    def fetch_submission_history(self) -> List[Dict]:
        """Fetches the complete submission history list."""
        offset = 0
        limit = 20
        all_submissions = []
        
        # Use rich status if console available
        status_context = self.console.status("[bold cyan]Fetching submission history...", spinner="dots") if self.console else None
        
        try:
            if status_context: status_context.__enter__()
            
            while True:
                data = self._gql_request(QUERY_SUBMISSION_LIST, {"offset": offset, "limit": limit}, "submissionList")
                if not data or "data" not in data or not data["data"]["submissionList"]:
                    break
                    
                sub_list = data["data"]["submissionList"]
                submissions = sub_list["submissions"]
                has_next = sub_list["hasNext"]
                
                all_submissions.extend(submissions)
                
                if status_context:
                    status_context.update(f"[bold cyan]Fetching submission history... (Fetched {len(all_submissions)} items)")
                
                if not has_next:
                    break
                    
                offset += limit
                time.sleep(0.5)
        finally:
            if status_context: status_context.__exit__(None, None, None)
            
        return all_submissions

    def harvest_all(self):
        """
        Main harvesting loop:
        1. Fetch History
        2. Group by Question
        3. For each question: Fetch Metadata + Submission Code
        4. Save to Disk
        """
        submissions_summary = self.fetch_submission_history()
        
        if self.console:
            self.console.print(f"[info]Total Submissions Found: [bold]{len(submissions_summary)}[/bold][/info]")

        # Group by slug
        grouped = defaultdict(list)
        for sub in submissions_summary:
            slug = sub.get("titleSlug")
            if slug:
                grouped[slug].append(sub)

        if self.console:
            self.console.print(f"[info]Unique Problems Attempted: [bold]{len(grouped)}[/bold][/info]")
            self.console.print("\n[bold]Starting detailed extraction...[/bold]")

        # Progress Bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            
            main_task = progress.add_task("[cyan]Processing Problems...", total=len(grouped))
            
            for i, (slug, subs) in enumerate(grouped.items(), 1):
                progress.update(main_task, description=f"[cyan]Processing: {slug}")
                
                # A. Fetch Metadata
                meta_response = self._gql_request(QUERY_PROBLEM_DETAILS, {"titleSlug": slug}, "selectProblem")
                if not meta_response or "data" not in meta_response:
                    question_data = {"error": "Failed to fetch"}
                else:
                    question_data = self._clean_data(meta_response["data"]["question"])
                
                # B. Fetch Submissions
                full_submissions = []
                for sub in subs:
                    sub_id = sub["id"]
                    detail_response = self._gql_request(QUERY_SUBMISSION_DETAILS, {"submissionId": sub_id}, "submissionDetails")
                    
                    if detail_response and "data" in detail_response and detail_response["data"]["submissionDetails"]:
                        cleaned_details = self._clean_data(detail_response["data"]["submissionDetails"])
                        full_sub = {**sub, **cleaned_details}
                        full_submissions.append(full_sub)
                    else:
                        full_submissions.append(sub)
                    
                    time.sleep(0.3) # Rate limit
                
                # Save
                final_output = {
                    "question_name": slug,
                    "problem_metadata": question_data,
                    "submissions": full_submissions
                }
                
                file_path = self.user_raw_dir / f"{slug}.json"
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(final_output, f, indent=2, ensure_ascii=False)
                
                progress.advance(main_task)
                time.sleep(0.5)

        if self.console:
            from rich.panel import Panel
            self.console.print(Panel(f"[bold green]Extraction Complete![/bold green]\nData saved to: {self.user_raw_dir}", title="Success", border_style="green"))
