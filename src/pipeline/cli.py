import os
import asyncio
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme
from pathlib import Path

from src.pipeline.config import ROOT_DIR
from src.pipeline.stage_1_harvester.authentication import LeetCodeAuthenticator, AuthenticationError
from src.pipeline.stage_1_harvester.harvester import LeetCodeHarvester

# Custom Rich Theme
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "highlight": "magenta",
})
console = Console(theme=custom_theme)

async def run_harvester(auth: LeetCodeAuthenticator, username: str):
    """
    Async wrapper for the harvesting process.
    Handles the main harvest loop and interactive retry logic.
    """
    async with auth.get_client() as client:
        harvester = LeetCodeHarvester(client, username, console)
        
        # 1. Initial Harvest
        failed_items = await harvester.harvest_all()
        
        # 2. Retry Loop
        while failed_items:
            count = len(failed_items)
            console.print(f"\n[warning]⚠️  {count} downloads failed.[/warning]")
            
            should_retry = await questionary.confirm(
                f"Do you want to retry these {count} failed items?",
                default=True
            ).ask_async()
            
            if not should_retry:
                console.print("[dim]Skipping retry. You can run the pipeline again later to retry.[/dim]")
                break
                
            # Run Retry logic
            await harvester.retry_failed(failed_items)
            
            # Check if any failed again
            failed_items = harvester.failed_slugs
            
            if not failed_items:
                console.print("[success]All retries successful![/success]")

def start():
    console.print(Panel.fit(
        "[bold cyan]LeetCode Data Extractor[/bold cyan]\n"
        "Extract your submissions, code, and problem metadata.",
        border_style="cyan"
    ))
    
    console.print("\n[bold]Please enter your LeetCode credentials:[/bold]")
    console.print("[dim](You can find these in your browser cookies/headers)[/dim]")
    
    session = questionary.password("LEETCODE_SESSION:").ask()
    csrf = questionary.text("csrftoken:").ask()
    cf = questionary.text("cf_clearance:").ask()
    
    if not session or not csrf or not cf:
        console.print("[error]All credentials are required![/error]")
        return

    console.print() # Spacer
    
    # Run Pipeline
    try:
        # 1. Authenticate (Synchronous check)
        auth = LeetCodeAuthenticator(session, csrf, cf)
        username = auth.validate()
        console.print(f"[success]Authenticated as: [bold]{username}[/bold][/success]")
        
        # 2. Harvest (Async Task)
        asyncio.run(run_harvester(auth, username))
            
    except AuthenticationError as e:
        console.print(f"[error]Authentication Failed: {e}[/error]")
    except Exception as e:
        console.print(f"[error]An unexpected error occurred: {e}[/error]")
        import traceback
        console.print(traceback.format_exc())

if __name__ == "__main__":
    start()
