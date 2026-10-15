from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
CLEAN_DIR = BASE_DIR / "data" / "clean"
DB_PATH = BASE_DIR / "data" / "scraped.db"


USER_AGENT = "LearningScraperBot/1.0 (+mailto:you@example.com)"

REQUEST_DELAY = 1.5
TIMEOUT = 15
MAX_RETRIES = 3
