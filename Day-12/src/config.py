import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Paths
STAGING_DIR = BASE_DIR / "data" / "staging"
CSV_PATH = BASE_DIR / "data" / "source" / "order_items.csv"
STATE_FILE = BASE_DIR / "state" / "watermark.json"
LOG_FILE = BASE_DIR / "logs" / "etl.log"
SNOWFLAKE_DDL = BASE_DIR / "sql" / "snowflake_setup.sql"

# PostgreSQL
PG = {
    "host": os.getenv("PG_HOST", "localhost"),
    "port": os.getenv("PG_PORT", "5432"),
    "db": os.getenv("PG_DB", "etl_source"),
    "user": os.getenv("PG_USER", "postgres"),
    "password": os.getenv("PG_PASSWORD", ""),
}

# Snowflake
SNOWFLAKE = {
    "account": os.getenv("SNOWFLAKE_ACCOUNT"),
    "user": os.getenv("SNOWFLAKE_USER"),
    "password": os.getenv("SNOWFLAKE_PASSWORD"),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
    "database": os.getenv("SNOWFLAKE_DATABASE", "ETL_DEMO").upper(),
    "role": os.getenv("SNOWFLAKE_ROLE"),
}

# API
API_URL = os.getenv("API_URL", "https://dummyjson.com/products")
API_PAGE_SIZE = int(os.getenv("API_PAGE_SIZE", "30"))

# Email alerts
ALERT_EMAIL_ENABLED = os.getenv("ALERT_EMAIL_ENABLED", "false").lower() == "true"
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
ALERT_TO = os.getenv("ALERT_TO")
