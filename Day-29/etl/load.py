"""Load: stage -> merge into core -> refresh mart -> audit."""
import uuid
from datetime import datetime, timezone

import pandas as pd
from snowflake.connector.pandas_tools import write_pandas

from etl.snowflake_client import run_sql, run_sql_file

STAGE_COLUMNS = ["order_id", "customer_id", "product", "category", "quantity", "unit_price",
                 "order_date", "status", "country", "gross_amount", "net_revenue"]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def new_batch_id() -> str:
    return f"{_utcnow():%Y%m%dT%H%M%S}_{uuid.uuid4().hex[:6]}"


def load_staging(conn, clean: pd.DataFrame, batch_id: str) -> int:
    """Bulk-load via Parquet + COPY (write_pandas) - far faster than row INSERTs."""
    df = clean[STAGE_COLUMNS].copy()
    df.columns = [c.upper() for c in df.columns]
    df["BATCH_ID"] = batch_id
    ok, _chunks, nrows, _ = write_pandas(
        conn, df, table_name="ORDERS_STG", schema="RAW",
        use_logical_type=True, quote_identifiers=False,
    )
    if not ok:
        raise RuntimeError("write_pandas reported failure")
    return nrows


def merge_core(conn, batch_id: str) -> None:
    run_sql_file(conn, "02_merge_core.sql", {"batch_id": batch_id})


def build_mart(conn, batch_id: str) -> None:
    run_sql_file(conn, "03_build_mart.sql", {"batch_id": batch_id})


def write_audit(conn, batch_id: str, started: datetime, raw_rows: int,
                clean_rows: int, reject_rows: int, status: str) -> None:
    run_sql(
        conn,
        "INSERT INTO AUDIT.PIPELINE_RUNS VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (batch_id, started, _utcnow(), raw_rows, clean_rows, reject_rows, status),
    )
