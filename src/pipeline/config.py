from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
env_path = ROOT_DIR / ".env"
load_dotenv(dotenv_path=env_path)
# The above code is not necessary as the .env file and the .env feature for saving credentials is removed officially.
# LeetCode Constants
GRAPHQL_URL = "https://leetcode.com/graphql/"
BASE_URL = "https://leetcode.com"

# Default Headers
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Referer": BASE_URL,
    "Origin": BASE_URL,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# Directories
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
LOGS_DIR = ROOT_DIR / "logs"

# Ensure dirs exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
