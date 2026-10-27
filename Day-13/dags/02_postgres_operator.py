from datetime import datetime

from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
# (SQLExecuteQueryOperator is the modern replacement of PostgresOperator)

with DAG(
    dag_id="02_postgres_operator",
    start_date=datetime(2024, 1, 1),
    schedule="@hourly",         # runs every hour
    catchup=False,
    tags=["day13"],
) as dag:

    create_table = SQLExecuteQueryOperator(
        task_id="create_table",
        conn_id="warehouse_db",
        sql="""
            CREATE TABLE IF NOT EXISTS task_log (
                id SERIAL PRIMARY KEY,
                run_date DATE,
                message TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """,
    )

    insert_row = SQLExecuteQueryOperator(
        task_id="insert_row",
        conn_id="warehouse_db",
        sql="INSERT INTO task_log (run_date, message) VALUES ('{{ ds }}', 'Hello from Airflow');",
    )

    create_table >> insert_row
