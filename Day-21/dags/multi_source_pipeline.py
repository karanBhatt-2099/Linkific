"""Day 21 - Multi-source collection pipeline.
extract (9 parallel tasks) -> convert formats -> load RAW to Snowflake -> integrate -> ANALYTICS
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from src import extract_api, extract_db, extract_files, extract_scrape, extract_sftp, integrate
from src.formats import convert_all
from src.load_snowflake import load_raw_tables
from src.utils import log, read_raw


def on_failure(context):
    log.error("Task %s FAILED: %s", context["task_instance"].task_id, context.get("exception"))


def convert_formats():
    for name in ["api_users", "sftp_customers", "pg_orders"]:
        convert_all(read_raw(name), name)


EXTRACTS = {
    "api_users": extract_api.api_users,
    "api_weather": extract_api.api_weather,
    "api_countries": extract_api.api_countries,
    "postgres": extract_db.postgres,
    "mongodb": extract_db.mongo,
    "files_csv": extract_files.csv_customers,
    "files_json": extract_files.file_orders,
    "files_excel": extract_files.file_targets,
    "web_scrape": extract_scrape.web_books,
    "sftp_xml": extract_sftp.sftp_customers,
}

with DAG(
    dag_id="day21_multi_source_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule="0 6 * * *",          # every day at 06:00
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=2), "on_failure_callback": on_failure},
    tags=["day21"],
) as dag:

    extract_tasks = [PythonOperator(task_id=f"extract_{n}", python_callable=fn) for n, fn in EXTRACTS.items()]
    convert = PythonOperator(task_id="convert_formats", python_callable=convert_formats)
    load_raw = PythonOperator(task_id="load_raw_to_snowflake", python_callable=load_raw_tables)
    integrate_task = PythonOperator(task_id="integrate_to_warehouse", python_callable=integrate.run)

    extract_tasks >> convert >> load_raw >> integrate_task
