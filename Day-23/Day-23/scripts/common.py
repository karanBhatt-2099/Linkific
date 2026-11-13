"""Shared helpers: logging, HTTP (retry + rate limit), staging, Snowflake load, watermark."""
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path

import requests
import snowflake.connector

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("ingestion")

STAGING = Path(os.getenv("STAGING_DIR", "/opt/airflow/data/staging"))


# ---------- HTTP: retries, backoff, 429 handling ----------
def http_get(url, params=None, headers=None, retries=3):
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=30)
            if r.status_code == 429:  # rate limited -> wait as long as the server asks
                wait = int(r.headers.get("Retry-After", 30))
                log.warning("429 rate limited on %s, sleeping %ss", url, wait)
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            log.warning("Attempt %s/%s failed for %s: %s", attempt, retries, url, e)
            if attempt == retries:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Gave up on {url} (kept getting rate limited)")


# ---------- Snowflake ----------
def get_conn():
    cfg = dict(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
    )
    if os.getenv("SNOWFLAKE_ROLE"):
        cfg["role"] = os.environ["SNOWFLAKE_ROLE"]
    return snowflake.connector.connect(**cfg)


def save_raw(name, records):
    """1) write records as NDJSON in data/staging/<name>/  2) load them into RAW_<NAME> in Snowflake."""
    if not records:
        log.warning("%s: no records, nothing to save", name)
        return 0

    folder = STAGING / name
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}_{datetime.utcnow():%Y%m%d_%H%M%S_%f}.json"
    with open(path, "w") as f:
        for r in records:
            f.write(json.dumps(r, default=str) + "\n")

    table = f"RAW_{name.upper()}"
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(f"CREATE TABLE IF NOT EXISTS {table} "
                    "(payload VARIANT, loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP())")
        cur.execute(f"PUT file://{path} @%{table} AUTO_COMPRESS=TRUE")          # upload to table stage
        cur.execute(f"COPY INTO {table}(payload) FROM (SELECT $1 FROM @%{table}) "
                    "FILE_FORMAT=(TYPE=JSON) PURGE=TRUE")                         # stage -> table
    finally:
        conn.close()

    log.info("%s: saved %s records -> %s and Snowflake.%s", name, len(records), path.name, table)
    return len(records)


# ---------- Incremental-load bookmark (stored in Snowflake) ----------
def get_watermark(source):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS ETL_WATERMARK (source STRING, last_value STRING)")
        cur.execute("SELECT last_value FROM ETL_WATERMARK WHERE source = %s", (source,))
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def set_watermark(source, value):
    conn = get_conn()
    try:
        conn.cursor().execute(
            "MERGE INTO ETL_WATERMARK t USING (SELECT %s AS source, %s AS last_value) s "
            "ON t.source = s.source "
            "WHEN MATCHED THEN UPDATE SET last_value = s.last_value "
            "WHEN NOT MATCHED THEN INSERT (source, last_value) VALUES (s.source, s.last_value)",
            (source, str(value)),
        )
    finally:
        conn.close()
