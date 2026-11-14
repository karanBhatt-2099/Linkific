"""Airflow DAG: extract -> quality_check -> transform -> load, once a day.

The steps hand data to each other through parquet files in ETL_STAGING_DIR, so that folder
must be shared storage (NFS, S3 mount, ...) if tasks run on different workers.
Make the `etl` package importable (put the project on PYTHONPATH or next to the dags folder).
"""
from datetime import datetime, timedelta

try:  # Airflow 3
    from airflow.sdk import DAG
    from airflow.providers.standard.operators.python import PythonOperator
except ImportError:  # Airflow 2
    from airflow import DAG
    from airflow.operators.python import PythonOperator

from etl import pipeline
from etl.alerts import notify_failure


def _spark():
    from etl.spark_session import get_spark

    return get_spark(with_snowflake=True)


def _extract():
    pipeline.extract(_spark())


def _quality_check():
    pipeline.quality_check(_spark())


def _transform():
    from etl.snowflake_io import SnowflakeSink

    pipeline.transform_data(_spark(), SnowflakeSink())


def _load():
    from etl.snowflake_io import SnowflakeSink

    pipeline.load_data(_spark(), SnowflakeSink())


default_args = {
    "owner": "data-engineering",
    "retries": 2,                          # retry logic: re-run a failed task twice...
    "retry_delay": timedelta(minutes=5),   # ...5 minutes apart
    "email_on_failure": True,              # needs Airflow's SMTP settings
    "on_failure_callback": notify_failure,  # our own alert email
}

with DAG(
    dag_id="hospital_etl",
    description="Hospital appointments: clean, validate, load incrementally into Snowflake",
    start_date=datetime(2026, 11, 1),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,  # never let two runs touch the same watermark
    default_args=default_args,
    tags=["etl", "hospital"],
) as dag:
    extract = PythonOperator(task_id="extract", python_callable=_extract)
    quality_check = PythonOperator(task_id="quality_check", python_callable=_quality_check)
    transform_data = PythonOperator(task_id="transform", python_callable=_transform)
    load_data = PythonOperator(task_id="load", python_callable=_load)

    extract >> quality_check >> transform_data >> load_data
