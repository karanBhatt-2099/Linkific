"""Callable steps shared by the Airflow DAG and the CLI (scripts/run_pipeline.py).

Steps hand data to each other through Parquet files in data/processed/<batch_id>/,
so each Airflow task is independently retryable.
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from etl import extract, load, quality, transform
from etl.config import PROCESSED_DIR, RAW_DIR
from etl.snowflake_client import get_connection

log = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _batch_dir(batch_id: str) -> Path:
    d = PROCESSED_DIR / batch_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def step_extract_transform(batch_id: str, raw_file: str | Path | None = None) -> dict:
    raw_file = Path(raw_file) if raw_file else RAW_DIR / "orders.csv"
    raw = extract.extract_orders(raw_file)
    clean, rejects = transform.transform_orders(raw)
    metrics = quality.check_dataframe(clean, rejects, raw_rows=len(raw))
    d = _batch_dir(batch_id)
    clean.to_parquet(d / "clean.parquet", index=False)
    rejects.to_csv(d / "rejects.csv", index=False)
    (d / "metrics.json").write_text(json.dumps({**metrics, "started": _utcnow().isoformat()}))
    log.info("Transform metrics: %s", metrics)
    return metrics


def step_load_staging(batch_id: str) -> int:
    clean = pd.read_parquet(_batch_dir(batch_id) / "clean.parquet")
    with get_connection() as conn:
        return load.load_staging(conn, clean, batch_id)


def step_merge_and_mart(batch_id: str) -> None:
    with get_connection() as conn:
        load.merge_core(conn, batch_id)
        load.build_mart(conn, batch_id)


def step_validate_and_audit(batch_id: str) -> dict:
    d = _batch_dir(batch_id)
    m = json.loads((d / "metrics.json").read_text())
    started = datetime.fromisoformat(m["started"])
    with get_connection() as conn:
        try:
            result = quality.check_snowflake(conn, batch_id, expected_rows=m["clean_rows"])
            status = "SUCCESS"
        except quality.DataQualityError:
            load.write_audit(conn, batch_id, started, m["raw_rows"], m["clean_rows"],
                             m["reject_rows"], "DQ_FAILED")
            raise
        load.write_audit(conn, batch_id, started, m["raw_rows"], m["clean_rows"],
                         m["reject_rows"], status)
    return result


def run_all(raw_file: str | Path | None = None, batch_id: str | None = None) -> dict:
    batch_id = batch_id or load.new_batch_id()
    out = {"batch_id": batch_id, "transform": step_extract_transform(batch_id, raw_file)}
    out["staged"] = step_load_staging(batch_id)
    step_merge_and_mart(batch_id)
    out["validation"] = step_validate_and_audit(batch_id)
    return out
