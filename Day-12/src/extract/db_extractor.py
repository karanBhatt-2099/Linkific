import pandas as pd
import psycopg2

from src import config
from src.utils.logger import get_logger
from src.utils.retry import retry

log = get_logger("extract.db")


def _query(sql: str, params=None) -> pd.DataFrame:
    p = config.PG
    conn = psycopg2.connect(host=p["host"], port=p["port"], dbname=p["db"],
                            user=p["user"], password=p["password"], connect_timeout=15)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            cols = [d[0] for d in cur.description]
            return pd.DataFrame(cur.fetchall(), columns=cols)
    finally:
        conn.close()


@retry(max_attempts=3)
def extract_customers() -> pd.DataFrame:
    """Full extract: the customer table is small."""
    df = _query("SELECT * FROM customers")
    log.info("Extracted %d customers from PostgreSQL", len(df))
    return df


@retry(max_attempts=3)
def extract_orders(since: str) -> pd.DataFrame:
    """Incremental extract: only orders created/changed after the watermark."""
    df = _query("SELECT * FROM orders WHERE updated_at > %s ORDER BY updated_at", (since,))
    log.info("Extracted %d new/changed orders (updated_at > %s)", len(df), since)
    return df
