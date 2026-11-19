"""Central configuration. All Snowflake settings come from environment variables (.env)."""
import os
from pathlib import Path

try:  # python-dotenv is optional inside Airflow (env_file already injects vars)
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass

BASE_DIR = Path(os.getenv("ETL_BASE_DIR", Path(__file__).resolve().parent.parent))
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
SQL_DIR = BASE_DIR / "sql"

REQUIRED_SNOWFLAKE_VARS = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_DATABASE",
]

# Business rules
VALID_STATUSES = {"completed", "pending", "cancelled", "refunded"}
REQUIRED_COLUMNS = [
    "order_id", "customer_id", "product", "category",
    "quantity", "unit_price", "order_date", "status", "country",
]


def snowflake_settings() -> dict:
    missing = [v for v in REQUIRED_SNOWFLAKE_VARS if not os.getenv(v)]
    if missing:
        raise EnvironmentError(f"Missing Snowflake env vars: {', '.join(missing)}")
    settings = {
        "account": os.environ["SNOWFLAKE_ACCOUNT"],
        "user": os.environ["SNOWFLAKE_USER"],
        "password": os.environ["SNOWFLAKE_PASSWORD"],
        "warehouse": os.environ["SNOWFLAKE_WAREHOUSE"],
        "database": os.environ["SNOWFLAKE_DATABASE"],
    }
    if os.getenv("SNOWFLAKE_ROLE"):
        settings["role"] = os.environ["SNOWFLAKE_ROLE"]
    return settings
