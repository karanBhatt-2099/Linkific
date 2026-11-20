# Product Inventory Pipeline (Airflow + Python + Snowflake + SQL)

API -> Python (CSV) -> Snowflake stage -> RAW.PRODUCTS -> SQL transform -> ANALYTICS.CATEGORY_SUMMARY -> DQ checks -> Power BI

## Run
1. `pip install -r requirements.txt`
2. Run `sql/01_setup.sql` in Snowflake
3. `cp .env.example .env && source .env` (fill in credentials)
4. Test each step: `python extract.py && python load_snowflake.py && python transform.py && python dq_checks.py`
5. Copy the project to your Airflow folder, set `PROJECT_DIR` in `dags/product_pipeline_dag.py`, trigger `product_pipeline`
6. In Power BI: Get Data -> Snowflake -> `PRODUCT_DB.ANALYTICS.CATEGORY_SUMMARY`

## Run Airflow in Docker
1. `cp .env.example .env` and fill in your Snowflake values
2. `docker compose up --build`
3. Open http://localhost:8080 (user `admin`, password: `docker compose exec airflow cat /opt/airflow/standalone_admin_password.txt`)
4. Turn on and trigger `product_pipeline`
5. Stop with `docker compose down`
