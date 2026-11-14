"""Central settings. Every value can be overridden with an environment variable."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Where the source CSV extracts land, and where the steps hand data to each other.
SOURCE_DIR = Path(os.getenv("ETL_SOURCE_DIR", BASE_DIR / "data" / "source"))
STAGING_DIR = Path(os.getenv("ETL_STAGING_DIR", BASE_DIR / "data" / "staging"))
LOG_DIR = Path(os.getenv("ETL_LOG_DIR", BASE_DIR / "logs"))

# Fail the run if more than this share of a table is rejected by the quality checks.
MAX_REJECT_RATIO = float(os.getenv("ETL_MAX_REJECT_RATIO", "0.5"))

# Snowflake connection (read from the environment, never hard-coded).
SNOWFLAKE = {
    "account": os.getenv("SNOWFLAKE_ACCOUNT"),
    "user": os.getenv("SNOWFLAKE_USER"),
    "password": os.getenv("SNOWFLAKE_PASSWORD"),
    "database": os.getenv("SNOWFLAKE_DATABASE", "HOSPITAL"),
    "schema": os.getenv("SNOWFLAKE_SCHEMA", "ANALYTICS"),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
    "role": os.getenv("SNOWFLAKE_ROLE"),
}

# Email alerts. If SMTP_HOST or ALERT_TO is empty, alerts are only logged.
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ALERT_FROM = os.getenv("ALERT_FROM", "etl-alerts@example.com")
ALERT_TO = os.getenv("ALERT_TO", "")
