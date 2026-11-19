"""Create schemas/tables in Snowflake (idempotent). Reads credentials from .env."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from etl.snowflake_client import get_connection, run_sql_file  # noqa: E402

if __name__ == "__main__":
    with get_connection() as conn:
        run_sql_file(conn, "01_setup.sql")
    print("Snowflake objects ready: RAW, CORE, MART, AUDIT")
