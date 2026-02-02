import questionary # This is a popular library used to create interactive terminal user interfaces (TIs
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme
# Rich is used for beautiful terminal output with colors and styles.
from src.pipeline.stage_1_harvester.authentication import LeetCodeAuthenticator, AuthenticationError # These two are the script files written for ensuring authentication.
from src.pipeline.stage_1_harvester.harvester import LeetCodeHarvester # The class inside harvester.py.

# Apparently this acts like the orchestrator for the pipeline in stage of data ingestion.
# Custom Rich Theme
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "highlight": "magenta",
})
console = Console(theme=custom_theme)
# This is the start function which is called from scripts/run_pipeline.py
def start():
    console.print(Panel.fit(
        "[bold cyan]LeetCode Data Extractor[/bold cyan]\n"
        "Extract your submissions, code, and problem metadata.",
        border_style="cyan"
    ))
    
    console.print("\n[bold]Please enter your LeetCode credentials:[/bold]")
    console.print("[dim](You can find these in your browser cookies/headers)[/dim]")
        
    session = questionary.password("LEETCODE_SESSION:").ask() # Hides teh input for security
    csrf = questionary.text("csrftoken:").ask()
    cf = questionary.text("cf_clearance:").ask()
        
    if not session or not csrf or not cf:
        console.print("[error]All credentials are required![/error]")
        return
        # The above is a precatutionary that checks that all credentials are provided.
    console.print() # Spacer
    
    # Run Pipeline
    try:
        # 1. Authenticate
        auth = LeetCodeAuthenticator(session, csrf, cf) # Creates and instance of the authenticator class.
        username = auth.validate() # Validate the credentials and get the username.
        console.print(f"[success]Authenticated as: [bold]{username}[/bold][/success]")
        
        # 2. Harvest
        # Get authenticated client
        with auth.get_client() as client:
            harvester = LeetCodeHarvester(client, username, console)
            harvester.harvest_all()
            
    except AuthenticationError as e:
        console.print(f"[error]Authentication Failed: {e}[/error]")
    except Exception as e:
        console.print(f"[error]An unexpected error occurred: {e}[/error]")
        import traceback
        console.print(traceback.format_exc()) # Prints the full traceback for debugging.

if __name__ == "__main__":
    start()
