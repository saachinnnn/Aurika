import asyncio
import os
from sqlalchemy import select
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv

from src.pipeline.database.connection import AsyncSessionLocal
from src.pipeline.database.models import SubmissionAnalysis, Submission

load_dotenv()
console = Console()

async def verify_analysis():
    console.print("[bold cyan]Verifying Submission Analysis Pipeline...[/bold cyan]")
    
    # 1. Check Environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        console.print(f"[success]ANTHROPIC_API_KEY found: {api_key[:8]}...[/success]")
    else:
        console.print("[warning]ANTHROPIC_API_KEY not found in .env[/warning]")

    async with AsyncSessionLocal() as session:
        # 2. Check for Analyses
        stmt = select(SubmissionAnalysis).limit(5)
        result = await session.execute(stmt)
        analyses = result.scalars().all()
        
        if not analyses:
            console.print("\n[warning]No submission analyses found in the database.[/warning]")
            console.print("Run the analyzer via CLI: [bold]python src/pipeline/cli.py[/bold] -> 'Analyze Submissions'")
            
            # Check if there are submissions to analyze
            sub_stmt = select(Submission).limit(1)
            sub_res = await session.execute(sub_stmt)
            if sub_res.scalars().first():
                console.print("[info]Submissions exist in the database, so analysis is possible.[/info]")
            else:
                console.print("[error]No submissions found in database either. Run 'Process Data' first.[/error]")
            return

        console.print(f"\n[success]Found {len(analyses)} analyses (showing first 5):[/success]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim")
        table.add_column("Sub ID")
        table.add_column("Approach")
        table.add_column("Time")
        table.add_column("Space")
        table.add_column("Mistake Type")
        table.add_column("Summary", width=50)

        for a in analyses:
            table.add_row(
                str(a.id),
                str(a.submission_id),
                a.approach_name,
                a.time_complexity,
                a.space_complexity,
                a.mistake_type or "N/A",
                a.analysis_summary[:47] + "..." if len(a.analysis_summary) > 50 else a.analysis_summary
            )
        
        console.print(table)

if __name__ == "__main__":
    asyncio.run(verify_analysis())
