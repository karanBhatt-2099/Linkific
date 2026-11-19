"""End-to-end tests.

- test_e2e_local: CSV -> extract -> transform -> DQ -> parquet, no external services.
- test_e2e_snowflake: full pipeline against Snowflake; skipped unless credentials are in env/.env.
- test_dag_integrity: DAG imports and has the expected shape; skipped if Airflow isn't installed.
"""
import os

import pandas as pd
import pytest

from etl.config import REQUIRED_SNOWFLAKE_VARS


def test_e2e_local(sample_csv, tmp_path, monkeypatch):
    from etl import pipeline
    monkeypatch.setattr(pipeline, "PROCESSED_DIR", tmp_path)
    m = pipeline.step_extract_transform("test_batch", sample_csv)
    clean = pd.read_parquet(tmp_path / "test_batch" / "clean.parquet")
    rejects = pd.read_csv(tmp_path / "test_batch" / "rejects.csv")
    assert len(clean) == m["clean_rows"] and len(rejects) == m["reject_rows"]
    assert m["clean_rows"] + m["reject_rows"] == m["raw_rows"]
    assert clean["order_id"].is_unique


def test_rerun_is_deterministic(sample_csv, tmp_path, monkeypatch):
    from etl import pipeline
    monkeypatch.setattr(pipeline, "PROCESSED_DIR", tmp_path)
    a = pipeline.step_extract_transform("a", sample_csv)
    b = pipeline.step_extract_transform("b", sample_csv)
    assert {k: a[k] for k in a} == {k: b[k] for k in b}


def test_dag_integrity():
    pytest.importorskip("airflow")
    from airflow.models import DagBag
    bag = DagBag(dag_folder="dags", include_examples=False)
    assert not bag.import_errors, bag.import_errors
    dag = bag.get_dag("orders_etl")
    assert {t.task_id for t in dag.tasks} == {
        "extract_transform", "load_staging", "merge_and_mart", "validate_and_audit"}
    assert dag.catchup is False and dag.max_active_runs == 1


@pytest.mark.skipif(not all(os.getenv(v) for v in REQUIRED_SNOWFLAKE_VARS),
                    reason="Snowflake credentials not set")
def test_e2e_snowflake(sample_csv):
    """Runs the pipeline twice on the same file: second run must be idempotent."""
    from etl import pipeline
    from etl.snowflake_client import get_connection, run_sql

    first = pipeline.run_all(sample_csv)
    with get_connection() as conn:
        n1 = run_sql(conn, "SELECT COUNT(*) FROM CORE.ORDERS")[0][0]
    second = pipeline.run_all(sample_csv)
    with get_connection() as conn:
        n2 = run_sql(conn, "SELECT COUNT(*) FROM CORE.ORDERS")[0][0]
    assert n1 == n2, "re-running the same data must not create duplicates"
    assert first["validation"]["core_revenue"] == second["validation"]["core_revenue"]
