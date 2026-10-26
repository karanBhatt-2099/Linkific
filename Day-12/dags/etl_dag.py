from datetime import datetime, timedelta

from airflow import DAG
from airflow.models.param import Param
from airflow.operators.python import PythonOperator

from src import pipeline
from src.utils.alerts import send_failure_email


def _alert_on_failure(context):
    ti = context["task_instance"]
    send_failure_email(
        f"Airflow task failed: {ti.dag_id}.{ti.task_id}",
        f"Run: {context['run_id']}\nTry: {ti.try_number}\nError: {context.get('exception')}",
    )


def _extract_orders(**context):
    pipeline.extract_orders(full_refresh=bool(context["params"]["full_refresh"]))


default_args = {
    "owner": "data-eng",
    "retries": 2,                          
    "retry_delay": timedelta(minutes=2),
    "on_failure_callback": _alert_on_failure,
}

with DAG(
    dag_id="etl_postgres_api_csv_to_snowflake",
    description="PostgreSQL + REST API + CSV -> staging -> transform -> Snowflake",
    start_date=datetime(2026, 10, 1),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,                     # tasks share the staging folder and watermark
    default_args=default_args,
    params={"full_refresh": Param(False, type="boolean",
                                  description="Reset the watermark and reload all orders")},
    tags=["etl", "snowflake"],
) as dag:

    extract_customers = PythonOperator(task_id="extract_customers", python_callable=pipeline.extract_customers)
    extract_orders = PythonOperator(task_id="extract_orders", python_callable=_extract_orders)
    extract_order_items = PythonOperator(task_id="extract_order_items", python_callable=pipeline.extract_order_items)
    extract_products = PythonOperator(task_id="extract_products", python_callable=pipeline.extract_products)

    transform = PythonOperator(task_id="transform", python_callable=pipeline.transform)
    load = PythonOperator(task_id="load_to_snowflake", python_callable=pipeline.load)

    [extract_customers, extract_orders, extract_order_items, extract_products] >> transform >> load
