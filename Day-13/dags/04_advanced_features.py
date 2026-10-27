import random
from datetime import datetime

from airflow.decorators import dag, task, task_group
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule


@dag(
    dag_id="04_advanced_features",
    start_date=datetime(2024, 1, 1),
    schedule="@weekly",         # runs once a week
    catchup=False,
    tags=["day13"],
)
def advanced():

    # ---- XCom: the return value is automatically pushed ----
    @task
    def pick_number():
        return random.randint(1, 100)

    # ---- XCom pulled with a template in a BashOperator ----
    show_number = BashOperator(
        task_id="show_number",
        bash_command="echo 'Number is {{ ti.xcom_pull(task_ids=\"pick_number\") }}'",
    )

    # ---- Branching: return the task_id to follow ----
    @task.branch
    def choose_path(number):
        return "even_path" if number % 2 == 0 else "odd_path"

    even_path = EmptyOperator(task_id="even_path")
    odd_path = EmptyOperator(task_id="odd_path")

    # ---- Trigger rule: run even though one branch was skipped ----
    join = EmptyOperator(
        task_id="join",
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    )

    # ---- Task group: tasks grouped in the UI ----
    @task_group
    def cleanup():
        step1 = BashOperator(task_id="clean_cache", bash_command="echo cleaning cache")
        step2 = BashOperator(task_id="clean_temp", bash_command="echo cleaning temp")
        step1 >> step2

    # ---- Trigger rule: always run at the end (success or fail) ----
    @task(trigger_rule=TriggerRule.ALL_DONE)
    def finish():
        print("Pipeline finished")

    number = pick_number()
    number >> show_number
    choose_path(number) >> [even_path, odd_path] >> join >> cleanup() >> finish()


advanced()
