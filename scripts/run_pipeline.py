import sys # This is the system basically for handling system related operations
from pathlib import Path # This is for handling file system paths in an object-oriented way.

# Add the project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir)) # Adding the project root directory to the system path to ensure that modules from the project can be imported correctly.

# The __file__ is the current path of the script file which is scripts/run_pipeline.py
## We are converting it to the absolute path and then getting its parent directory twice to reach the project root.
### .parent goes up one level to the scripts directory and the another .parent goes up to the project root.


from src.pipeline.cli import start # Remember, cli.py is inside src/pipeline directory and its the orchestrator file.

if __name__ == "__main__":
    start()
