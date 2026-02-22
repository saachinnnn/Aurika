import json
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.pipeline.config import RAW_DATA_DIR

console = Console()

def check_integrity(username="saachinnnnn"):
    user_dir = RAW_DATA_DIR / username
    if not user_dir.exists():
        console.print(f"[red]Directory not found: {user_dir}[/red]")
        return

    files = list(user_dir.glob("*.json"))
    console.print(f"Checking {len(files)} files for user: [bold cyan]{username}[/bold cyan]...\n")

    passed = 0
    failed_files = []

    for file_path in files:
        if file_path.name in ["manifest.json", "failed_downloads.json"]:
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            errors = []

            # 1. Check Metadata
            meta = data.get("problem_metadata", {})
            if not meta.get("content"):
                errors.append("Missing Problem Content")
            if not meta.get("difficulty"):
                errors.append("Missing Difficulty")

            # 2. Check Submissions
            subs = data.get("submissions", [])
            if not subs:
                errors.append("No Submissions Found")
            else:
                # Check for Code in AT LEAST one submission (or all?)
                # Ideally all should have code if we fetched details.
                missing_code_count = 0
                for sub in subs:
                    if "code" not in sub:
                        missing_code_count += 1

                if missing_code_count > 0:
                    errors.append(f"Missing Code in {missing_code_count}/{len(subs)} submissions")

            if errors:
                failed_files.append({"file": file_path.name, "errors": errors})
            else:
                passed += 1

        except Exception as e:
            failed_files.append({"file": file_path.name, "errors": [f"JSON Error: {str(e)}"]})

    # Report
    table = Table(title="Data Integrity Report")
    table.add_column("File", style="cyan")
    table.add_column("Issues", style="red")

    for fail in failed_files:
        table.add_row(fail["file"], ", ".join(fail["errors"]))

    if failed_files:
        console.print(table)

    console.print(f"\n[bold green]PASSED: {passed}[/bold green]")
    console.print(f"[bold red]FAILED: {len(failed_files)}[/bold red]")
    console.print(f"Total: {len(files) - 2}") # Subtract manifest/failed

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", default="saachinnnnn", help="Username to check")
    args = parser.parse_args()

    check_integrity(args.user)
