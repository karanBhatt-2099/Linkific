"""Airflow DAG: extract -> load -> transform -> quality check (runs daily)."""
import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

PROJECT_DIR = "/opt/airflow/product_pipeline"   # <-- change to your project path
sys.path.append(PROJECT_DIR)

from extract import extract                      # noqa: E402
from load_snowflake import load                  # noqa: E402
from transform import transform                  # noqa: E402
from dq_checks import run_checks                 # noqa: E402

default_args = {
    "owner": "data_engineer",
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="product_pipeline",
    default_args=default_args,
    start_date=datetime(2026, 11, 1),
    schedule="@daily",
    catchup=False,
) as dag:

    t1 = PythonOperator(task_id="extract_from_api", python_callable=extract,
                        op_kwargs={"path": "/tmp/products.csv"})
    t2 = PythonOperator(task_id="load_to_snowflake", python_callable=load,
                        op_kwargs={"path": "/tmp/products.csv"})
    t3 = PythonOperator(task_id="transform_sql", python_callable=transform,
                        op_kwargs={"sql_file": f"{PROJECT_DIR}/sql/02_transform.sql"})
    t4 = PythonOperator(task_id="data_quality_checks", python_callable=run_checks)

    t1 >> t2 >> t3 >> t4
