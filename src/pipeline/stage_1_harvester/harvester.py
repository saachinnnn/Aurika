import json
import asyncio
import logging
import httpx
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

CONCURRENCY_LIMIT = 25  # Max parallel requests

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
    def __init__(self, client: httpx.AsyncClient, username: str, console: Optional[Console] = None):
        self.client = client
        self.username = username
        self.console = console or Console()
        self.user_raw_dir = RAW_DATA_DIR / username
        self.user_raw_dir.mkdir(parents=True, exist_ok=True)
        self.semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
        self.failed_slugs: List[Dict[str, str]] = []

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

    async def _gql_request(self, query: str, variables: dict, operation_name: str) -> Optional[dict]:
        try:
            response = await self.client.post(
                GRAPHQL_URL,
                json={"query": query, "variables": variables, "operationName": operation_name}
            )
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                logger.error(f"GraphQL Error in {operation_name}: {data['errors']}")
                return None
                
            return data
        except httpx.HTTPError as e:
            logger.error(f"Request failed for {operation_name}: {e}")
            return None

    def _save_manifest(self, slugs: List[str]):
        """Saves the list of problems to be fetched (Checkpoint Phase A)."""
        manifest_path = self.user_raw_dir / "manifest.json"
        try:
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump({"problems": slugs, "count": len(slugs)}, f, indent=2)
            if self.console:
                self.console.print(f"[info]Manifest saved to {manifest_path}[/info]")
        except Exception as e:
            logger.error(f"Failed to save manifest: {e}")

    def _save_failed(self):
        """Saves the list of failed downloads to disk."""
        if not self.failed_slugs:
            return
            
        failed_path = self.user_raw_dir / "failed_downloads.json"
        try:
            with open(failed_path, "w", encoding="utf-8") as f:
                json.dump(self.failed_slugs, f, indent=2)
            if self.console:
                self.console.print(f"[warning]Saved {len(self.failed_slugs)} failed items to {failed_path}[/warning]")
        except Exception as e:
            logger.error(f"Failed to save dead letter queue: {e}")

    async def fetch_submission_history(self) -> List[Dict]:
        """Fetches the complete submission history list."""
        offset = 0
        limit = 20
        all_submissions = []
        
        status_context = self.console.status("[bold cyan]Fetching submission history...", spinner="dots") if self.console else None
        
        try:
            if status_context: status_context.__enter__()
            
            while True:
                # List fetching is sequential because of pagination dependency
                data = await self._gql_request(QUERY_SUBMISSION_LIST, {"offset": offset, "limit": limit}, "submissionList")
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
                await asyncio.sleep(0.2) # Small delay for list paging
        finally:
            if status_context: status_context.__exit__(None, None, None)
            
        return all_submissions

    async def process_problem(self, slug: str, subs: List[Dict], progress: Progress, task_id: Any):
        """
        Fetches metadata and details for a single problem.
        Controlled by semaphore for concurrency.
        """
        async with self.semaphore:
            try:
                progress.update(task_id, description=f"[cyan]Processing: {slug}")
                
                # A. Fetch Metadata
                meta_response = await self._gql_request(QUERY_PROBLEM_DETAILS, {"titleSlug": slug}, "selectProblem")
                if not meta_response or "data" not in meta_response:
                    raise Exception("Failed to fetch problem metadata")
                
                question_data = self._clean_data(meta_response["data"]["question"])
                
                # B. Fetch Submissions (Sequential per problem)
                full_submissions = []
                for sub in subs:
                    sub_id = sub["id"]
                    detail_response = await self._gql_request(QUERY_SUBMISSION_DETAILS, {"submissionId": sub_id}, "submissionDetails")
                    
                    if detail_response and "data" in detail_response and detail_response["data"]["submissionDetails"]:
                        cleaned_details = self._clean_data(detail_response["data"]["submissionDetails"])
                        full_sub = {**sub, **cleaned_details}
                        full_submissions.append(full_sub)
                    else:
                        full_submissions.append(sub)
                    
                    await asyncio.sleep(0.1)
                
                # Save
                final_output = {
                    "question_name": slug,
                    "problem_metadata": question_data,
                    "submissions": full_submissions
                }
                
                file_path = self.user_raw_dir / f"{slug}.json"
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(final_output, f, indent=2, ensure_ascii=False)
                
                progress.advance(task_id)
                
            except Exception as e:
                # Dead Letter Logic
                logger.error(f"Failed to process {slug}: {e}")
                self.failed_slugs.append({"slug": slug, "error": str(e), "submissions": subs})
                if self.console:
                    self.console.print(f"[red]Failed: {slug} ({e})[/red]")
            finally:
                # Post-task cooldown to respect rate limits globally
                await asyncio.sleep(0.1)

    async def harvest_all(self) -> List[Dict]:
        """
        Main harvesting loop: Concurrent execution.
        Returns list of failed items.
        """
        submissions_summary = await self.fetch_submission_history()
        
        if self.console:
            self.console.print(f"[info]Total Submissions Found: [bold]{len(submissions_summary)}[/bold][/info]")

        # Group by slug
        grouped = defaultdict(list)
        for sub in submissions_summary:
            slug = sub.get("titleSlug")
            if slug:
                grouped[slug].append(sub)

        unique_slugs = list(grouped.keys())
        self._save_manifest(unique_slugs)

        if self.console:
            self.console.print(f"[info]Unique Problems Attempted: [bold]{len(grouped)}[/bold][/info]")
            self.console.print(f"\n[bold]Starting concurrent extraction (Max {CONCURRENCY_LIMIT} threads)...[/bold]")

        # Progress Bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            
            main_task = progress.add_task("[cyan]Processing Problems...", total=len(grouped))
            
            # Create tasks
            tasks = []
            for slug, subs in grouped.items():
                tasks.append(self.process_problem(slug, subs, progress, main_task))
            
            # Run concurrently
            await asyncio.gather(*tasks)

        self._save_failed()

        if self.console:
            from rich.panel import Panel
            msg = f"[bold green]Extraction Complete![/bold green]\nData saved to: {self.user_raw_dir}"
            if self.failed_slugs:
                msg += f"\n[bold red]Failures: {len(self.failed_slugs)}[/bold red] (See failed_downloads.json)"
            self.console.print(Panel(msg, title="Success", border_style="green"))
            
        return self.failed_slugs

    async def retry_failed(self, failed_items: List[Dict]):
        """
        Retries only the failed items using the same concurrency logic.
        """
        if not failed_items:
            return

        self.failed_slugs = [] # Reset failure tracking for this run
        
        if self.console:
            self.console.print(f"\n[bold yellow]Retrying {len(failed_items)} failed items...[/bold yellow]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            
            main_task = progress.add_task("[yellow]Retrying...", total=len(failed_items))
            tasks = []
            
            for item in failed_items:
                slug = item["slug"]
                subs = item["submissions"] # We preserved the submissions list!
                tasks.append(self.process_problem(slug, subs, progress, main_task))
            
            await asyncio.gather(*tasks)
            
        self._save_failed() # Save any that failed again
