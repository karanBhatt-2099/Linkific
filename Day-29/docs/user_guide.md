# User Guide

## Prerequisites
Docker + Docker Compose, a Snowflake account with a role that can create objects in the target database, Python 3.11+ (only for running tests/scripts locally).

## 1. Configure credentials
```bash
cp .env.example .env
# edit .env: SNOWFLAKE_ACCOUNT, USER, PASSWORD, ROLE, WAREHOUSE, DATABASE
```
Generate a Fernet key for Airflow (optional but recommended) and paste into `AIRFLOW__CORE__FERNET_KEY`:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
The database in `SNOWFLAKE_DATABASE` must already exist (`CREATE DATABASE ETL_DEMO;`).

## 2. Create Snowflake objects (once)
```bash
pip install -r requirements.txt
python scripts/setup_snowflake.py
```

## 3. Get sample data
```bash
python scripts/generate_sample_data.py --rows 1000      # writes data/raw/orders.csv
```
Or drop your own `orders.csv` with the columns in the data dictionary.

## 4. Start Airflow
```bash
docker compose up --build -d
```
Open http://localhost:8080 (user/password from `.env`, default admin/admin). Un-pause the `orders_etl` DAG and click **Trigger**. Watch the 4 tasks go green.

## 5. Check results in Snowflake
```sql
SELECT * FROM AUDIT.PIPELINE_RUNS ORDER BY STARTED_AT DESC;
SELECT * FROM MART.DAILY_SALES ORDER BY ORDER_DATE DESC LIMIT 20;
```
Rejected rows: `data/processed/<batch_id>/rejects.csv`.

## 6. Dashboard (optional)
```bash
docker compose --profile dashboard up dashboard
```
Open http://localhost:8501. Filters in the sidebar; data cached for 5 minutes.

## Run without Airflow
```bash
python scripts/run_pipeline.py --dry-run     # no Snowflake needed
python scripts/run_pipeline.py               # full run
```

## Run tests
```bash
python -m pytest              # Snowflake and Airflow tests skip automatically if unavailable
```

## Troubleshooting
| Symptom | Fix |
|---|---|
| `Missing Snowflake env vars` | Check `.env` is next to `docker-compose.yml`; rebuild/restart containers |
| `250001` / login error | Wrong account identifier format; use `<orgname>-<account>` |
| DAG not visible | `docker compose logs airflow-scheduler`; check import errors |
| `reject ratio exceeds 20%` | Source data quality problem; open `rejects.csv` |
| Permission denied on `logs/` | Set `AIRFLOW_UID` in `.env` to your user id (`id -u` on Linux) |
| Warehouse costs | `ETL_WH` is XSMALL with 60 s auto-suspend; suspend manually when done |
