"""Orders ETL: CSV -> transform -> Snowflake RAW -> CORE (MERGE) -> MART, with DQ gates.

Schedule: daily. Each run uses its Airflow run_id as the batch id, so retries/re-runs are
idempotent (same batch -> same MERGE result).
"""
import re
from datetime import datetime, timedelta

from airflow.decorators import dag, task

from etl import pipeline

DEFAULT_ARGS = {
    "owner": "data-eng",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "retry_exponential_backoff": True,
}


def _batch_id(run_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", run_id)[:60]   # safe for file names and SQL literals


@dag(
    dag_id="orders_etl",
    description="Small orders ETL into Snowflake",
    start_date=datetime(2026, 11, 1),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,
    default_args=DEFAULT_ARGS,
    tags=["etl", "snowflake", "orders"],
    doc_md=__doc__,
)
def orders_etl():
    @task
    def extract_transform(run_id=None) -> str:
        batch_id = _batch_id(run_id)
        pipeline.step_extract_transform(batch_id)
        return batch_id

    @task
    def load_staging(batch_id: str) -> str:
        pipeline.step_load_staging(batch_id)
        return batch_id

    @task
    def merge_and_mart(batch_id: str) -> str:
        pipeline.step_merge_and_mart(batch_id)
        return batch_id

    @task
    def validate_and_audit(batch_id: str) -> dict:
        return pipeline.step_validate_and_audit(batch_id)

    validate_and_audit(merge_and_mart(load_staging(extract_transform())))


orders_etl()
