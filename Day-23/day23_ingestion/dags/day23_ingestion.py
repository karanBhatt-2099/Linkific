"""Day 23 - orchestrates every source into the staging area (local files + Snowflake RAW tables)."""
import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.exceptions import AirflowFailException
from airflow.operators.python import PythonOperator

from scripts import api_collect, db_extract, file_collect, scrape_collect

log = logging.getLogger("ingestion")

SOURCES = {
    "api_posts": api_collect.collect_posts,
    "api_github": api_collect.collect_github,
    "api_crypto": api_collect.collect_crypto,
    "scrape_books": scrape_collect.scrape_books,
    "scrape_quotes": scrape_collect.scrape_quotes,
    "files": file_collect.process_files,
    "db_orders": db_extract.extract_orders,
}


def log_failure(context):
    log.error("TASK FAILED: %s | %s", context["task_instance"].task_id, context.get("exception"))


def summary(**context):
    """Runs even if sources failed; logs the result and fails the DAG run if any source failed."""
    tis = context["dag_run"].get_task_instances()
    failed = [t.task_id for t in tis if t.task_id != "summary" and t.state != "success"]
    log.info("Ingestion finished. OK: %s | FAILED: %s", len(SOURCES) - len(failed), failed)
    if failed:
        raise AirflowFailException(f"Failed sources: {failed}")


with DAG(
    dag_id="day23_ingestion",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=1),
        "on_failure_callback": log_failure,
    },
) as dag:
    jobs = [PythonOperator(task_id=name, python_callable=fn) for name, fn in SOURCES.items()]
    done = PythonOperator(task_id="summary", python_callable=summary, trigger_rule="all_done")
    jobs >> done  # each source is independent; one failing doesn't stop the others
