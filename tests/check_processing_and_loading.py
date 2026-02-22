import asyncio
import sys
import os
from sqlalchemy import select, func, inspect
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

# Add project root to python path
sys.path.append(os.getcwd())

from src.pipeline.database.connection import AsyncSessionLocal
from src.pipeline.database.models import User, Problem, Submission, ProblemTopic, SubmissionAnalysis, TopicPrerequisite

console = Console()

def truncate(text, length=30):
    if text is None:
        return "None"
    s = str(text)
    if len(s) > length:
        return s[:length] + "..."
    return s

async def verify_pipeline_data():
    """
    Comprehensive verification script to check if data has been correctly loaded
    into all tables in the database, showing all requested columns.
    """
    console.print(Panel.fit("[bold cyan]Database Verification Script (Full Columns)[/bold cyan]", border_style="cyan"))

    async with AsyncSessionLocal() as session:
        # ---------------------------------------------------------------------
        # 1. Verify Users Table
        # ---------------------------------------------------------------------
        console.print("\n[bold yellow]1. Verifying 'users' Table (Filtering for '_prxnxv')[/bold yellow]")
        result = await session.execute(select(User).where(User.username == "_prxnxv"))
        users = result.scalars().all()
        
        if not users:
            console.print("[red]FAIL User '_prxnxv' not found![/red]")
            return # Exit early if user not found as other checks depend on it contextually
        else:
            table = Table(title=f"Users Found ({len(users)})", show_lines=True)
            # Columns: id, username, real_name, leetcode_session, leetcode_csrf, level, total_problems, total_submissions, last_sync_at, created_at
            table.add_column("id", style="dim")
            table.add_column("username", style="green")
            table.add_column("real_name")
            table.add_column("leetcode_session")
            table.add_column("leetcode_csrf")
            table.add_column("level")
            table.add_column("total_problems")
            table.add_column("total_submissions")
            table.add_column("last_sync_at")
            table.add_column("created_at")
            
            user_id = users[0].id # Capture ID for filtering submissions later

            for user in users:
                table.add_row(
                    str(user.id),
                    user.username,
                    str(user.real_name),
                    truncate(user.leetcode_session),
                    truncate(user.leetcode_csrf),
                    str(user.level),
                    str(user.total_problems),
                    str(user.total_submissions),
                    str(user.last_sync_at),
                    str(user.created_at)
                )
            console.print(table)

        # ---------------------------------------------------------------------
        # 2. Verify Problems Table (Sample)
        # ---------------------------------------------------------------------
        console.print("\n[bold yellow]2. Verifying 'problems' Table (Sample of 5)[/bold yellow]")
        total_problems = await session.scalar(select(func.count(Problem.id)))
        
        if total_problems == 0:
            console.print("[red]FAIL No problems found![/red]")
        else:
            result = await session.execute(select(Problem).limit(5))
            problems = result.scalars().all()
            
            table = Table(title=f"Problems Sample (Total: {total_problems})", show_lines=True)
            # Columns: id, title, title_slug, difficulty, content_html, acceptance_rate, total_accepted, total_submissions, hints (via raw), raw_api_response, created_at, updated_at
            table.add_column("id", style="dim")
            table.add_column("title", style="blue")
            table.add_column("title_slug")
            table.add_column("difficulty")
            table.add_column("content_html")
            table.add_column("acceptance_rate")
            table.add_column("total_accepted")
            table.add_column("total_submissions")
            table.add_column("hints (raw)")
            table.add_column("raw_api_response")
            table.add_column("created_at")
            table.add_column("updated_at")
            
            for p in problems:
                # Extract hints from raw_api_response if available
                hints = "N/A"
                if p.raw_api_response and "hints" in p.raw_api_response:
                    hints = str(p.raw_api_response["hints"])

                table.add_row(
                    p.id,
                    p.title,
                    p.title_slug,
                    p.difficulty,
                    truncate(p.content_html, 20),
                    f"{p.acceptance_rate}%" if p.acceptance_rate else "N/A",
                    str(p.total_accepted),
                    str(p.total_submissions),
                    truncate(hints, 20),
                    truncate(str(p.raw_api_response), 20),
                    str(p.created_at),
                    str(p.updated_at)
                )
            console.print(table)

        # ---------------------------------------------------------------------
        # 3. Verify Problem Topics (Sample)
        # ---------------------------------------------------------------------
        console.print("\n[bold yellow]3. Verifying 'problem_topics' Table (Sample of 5)[/bold yellow]")
        total_topics = await session.scalar(select(func.count(ProblemTopic.problem_id))) 
        
        if total_topics == 0:
            console.print("[red]FAIL No problem topics found![/red]")
        else:
            result = await session.execute(select(ProblemTopic).limit(5))
            topics = result.scalars().all()
            
            table = Table(title=f"Problem Topics Sample (Total Associations: {total_topics})", show_lines=True)
            # Columns: problem_id, topic_name, topic_slug
            table.add_column("problem_id", style="dim")
            table.add_column("topic_name", style="magenta")
            table.add_column("topic_slug")
            
            for t in topics:
                table.add_row(t.problem_id, t.topic_name, t.topic_slug)
            console.print(table)

        # ---------------------------------------------------------------------
        # 4. Verify Submissions Table (Sample)
        # ---------------------------------------------------------------------
        console.print("\n[bold yellow]4. Verifying 'submissions' Table (Sample of 5 for '_prxnxv')[/bold yellow]")
        
        # Count total submissions for this user
        total_submissions = await session.scalar(
            select(func.count(Submission.id)).where(Submission.user_id == user_id)
        )
        
        if total_submissions == 0:
            console.print("[red]FAIL No submissions found for user '_prxnxv'![/red]")
        else:
            result = await session.execute(
                select(Submission).where(Submission.user_id == user_id).limit(5)
            )
            submissions = result.scalars().all()
            
            table = Table(title=f"Submissions Sample (Total: {total_submissions})", show_lines=True)
            # Columns: id, user_id, problem_id, status, status_code, language, runtime_ms, runtime_percentile, memory_bytes, memory_percentile, code, timestamp, attempt_number, runtime_error, compile_error, raw_api_response, created_at
            table.add_column("id", style="dim")
            table.add_column("user_id", style="dim")
            table.add_column("problem_id")
            table.add_column("status", style="bold")
            table.add_column("status_code")
            table.add_column("language")
            table.add_column("runtime_ms")
            table.add_column("runtime_percentile")
            table.add_column("memory_bytes")
            table.add_column("memory_percentile")
            table.add_column("code")
            table.add_column("timestamp")
            table.add_column("attempt_number")
            table.add_column("runtime_error")
            table.add_column("compile_error")
            table.add_column("raw_api_response")
            table.add_column("created_at")
            
            for s in submissions:
                status_style = "green" if s.status == "Accepted" else "red"
                table.add_row(
                    s.id,
                    str(s.user_id),
                    s.problem_id,
                    f"[{status_style}]{s.status}[/{status_style}]",
                    str(s.status_code),
                    s.language,
                    str(s.runtime_ms),
                    str(s.runtime_percentile),
                    str(s.memory_bytes),
                    str(s.memory_percentile),
                    truncate(s.code, 20),
                    str(s.timestamp),
                    str(s.attempt_number),
                    truncate(s.runtime_error, 20),
                    truncate(s.compile_error, 20),
                    truncate(str(s.raw_api_response), 20),
                    str(s.created_at)
                )
            console.print(table)

        # ---------------------------------------------------------------------
        # 5. Verify Submission Analysis (Sample)
        # ---------------------------------------------------------------------
        console.print("\n[bold yellow]5. Verifying 'submission_analyses' Table[/bold yellow]")
        total_analyses = await session.scalar(select(func.count(SubmissionAnalysis.submission_id)))
        
        if total_analyses == 0:
            console.print("[dim]Info: No submission analyses found (Expected if analysis pipeline hasn't run yet)[/dim]")
        else:
            result = await session.execute(select(SubmissionAnalysis).limit(5))
            analyses = result.scalars().all()
            
            table = Table(title=f"Analyses Sample (Total: {total_analyses})", show_lines=True)
            # Columns: submission_id, approach_name, approach_category, time_complexity, space_complexity, is_optimal, interview_score, mistake_type, mistake_detail, analysis_summary, llm_model_used, analyzed_at
            table.add_column("submission_id")
            table.add_column("approach_name")
            table.add_column("approach_category")
            table.add_column("time_complexity")
            table.add_column("space_complexity")
            table.add_column("is_optimal")
            table.add_column("interview_score")
            table.add_column("mistake_type")
            table.add_column("mistake_detail")
            table.add_column("analysis_summary")
            table.add_column("llm_model_used")
            table.add_column("analyzed_at")
            
            for a in analyses:
                table.add_row(
                    a.submission_id,
                    str(a.approach_name),
                    str(a.approach_category),
                    str(a.time_complexity),
                    str(a.space_complexity),
                    str(a.is_optimal),
                    str(a.interview_score),
                    str(a.mistake_type),
                    truncate(a.mistake_detail, 20),
                    truncate(a.analysis_summary, 20),
                    str(a.llm_model_used),
                    str(a.analyzed_at)
                )
            console.print(table)

        # ---------------------------------------------------------------------
        # 6. Verify Topic Prerequisites (Sample)
        # ---------------------------------------------------------------------
        console.print("\n[bold yellow]6. Verifying 'topic_prerequisites' Table[/bold yellow]")
        # Note: This table might be empty if not populated by a specific loader yet
        try:
            total_prereqs = await session.scalar(select(func.count(TopicPrerequisite.topic_slug)))
        except Exception:
            total_prereqs = 0
            
        if total_prereqs == 0:
             console.print("[dim]Info: No topic prerequisites found (Expected if static data hasn't been loaded)[/dim]")
        else:
            result = await session.execute(select(TopicPrerequisite).limit(5))
            prereqs = result.scalars().all()
            
            table = Table(title=f"Topic Prerequisites Sample (Total: {total_prereqs})", show_lines=True)
            # Columns: topic_slug, prerequisite_of_slug
            table.add_column("topic_slug")
            table.add_column("prerequisite_of_slug")
            
            for p in prereqs:
                table.add_row(p.topic_slug, p.prerequisite_of_slug)
            console.print(table)

    console.print("\n[bold cyan]Verification Complete[/bold cyan]")

if __name__ == "__main__":
    asyncio.run(verify_pipeline_data())
