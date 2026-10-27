from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from hello_operator import HelloOperator  # from /plugins


def say_hi():
    print("Hi from PythonOperator!")


with DAG(
    dag_id="01_basic_operators",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",          # runs once a day
    catchup=False,              # don't run for past dates
    tags=["day13"],
) as dag:

    bash_task = BashOperator(task_id="print_date", bash_command="date")
    python_task = PythonOperator(task_id="say_hi", python_callable=say_hi)
    custom_task = HelloOperator(task_id="hello_custom", name="Airflow")

    bash_task >> python_task >> custom_task
