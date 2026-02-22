import os
import asyncio
import traceback
from pathlib import Path
from typing import Optional

from src.pipeline.database.connection import AsyncSessionLocal
from src.pipeline.processing.parser import parse_file
from src.pipeline.processing.loader import load_data

async def run_pipeline(data_dir: str):
    """
    Runs the ETL pipeline:
    1. Iterates over all JSON files in the data directory.
    2. Parses each file into Pydantic models.
    3. Loads the data into the database with upsert logic.
    """
    data_path = Path(data_dir)
    if not data_path.exists():
        print(f"Error: Directory {data_dir} does not exist.")
        return

    # Find all JSON files recursively
    json_files = [f for f in data_path.rglob("*.json") if f.name != "manifest.json"]
    
    if not json_files:
        print(f"No JSON files found in {data_dir}")
        return

    print(f"Found {len(json_files)} JSON files to process.")

    async with AsyncSessionLocal() as session:
        for file_path in json_files:
            try:
                print(f"Processing {file_path.name}...")
                
                # 1. Parse (CPU bound, but fast enough for now to run in main loop)
                # If very heavy, could run in executor
                parsed_data = parse_file(str(file_path))
                
                # 2. Load (Async DB I/O)
                await load_data(session, parsed_data)
                
                # Log stats
                problem = parsed_data['problem']
                submissions = parsed_data['submissions']
                print(f"  -> Loaded problem '{problem.title}' with {len(submissions)} submissions.")
                
            except Exception as e:
                print(f"  -> Error processing {file_path.name}: {e}")
                traceback.print_exc()
                await session.rollback() 
                continue

    print("Pipeline execution completed.")
