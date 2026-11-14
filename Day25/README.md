# Hospital Appointments ETL

PySpark transforms, Airflow orchestration, Snowflake storage.
Source: three CSV extracts (`patients`, `doctors`, `appointments`) in `data/source/`.

```
extract  ->  quality_check  ->  transform  ->  load
 clean        good/rejected      join, rules,    MERGE into Snowflake,
 + cast       split              aggregate,      then move the watermark
                                 pick changes
```

Each step reads the previous step's parquet files from `data/staging/`, so Airflow runs them as four tasks.

## Layout

| Path | What it does |
|---|---|
| `etl/transform.py` | Cleaning, type conversion, age / fee band / revenue rules, join, monthly doctor summary |
| `etl/quality.py` | Data quality framework: null, range, format, duplicate and referential integrity checks |
| `etl/incremental.py` | Timestamp-based change capture, watermark helper, Snowflake `MERGE` builder |
| `etl/snowflake_io.py` | All Snowflake access (watermark, upsert, replace), wrapped in retries |
| `etl/pipeline.py` | The four steps and `run_pipeline()` |
| `etl/retry.py`, `etl/alerts.py`, `etl/logger.py` | Retry with backoff, email alerts, logging to console and `logs/etl.log` |
| `dags/hospital_etl_dag.py` | Airflow DAG (daily, 2 retries, failure email) |
| `sql/create_tables.sql` | Snowflake tables, run once |
| `tests/` | Unit, integration and data validation tests |

## How the requirements are covered

- **Data quality**: every check adds a flag column; rows that fail go to `data/staging/rejected/<table>` with a `dq_errors` column naming the broken rules. The run stops if more than `ETL_MAX_REJECT_RATIO` (default 50%) of a table is rejected.
- **Incremental loading**: a row is changed when `updated_at` is newer than the table's value in `ETL_WATERMARK`. Changed rows go to a staging table and are `MERGE`d: update if present, insert if new, delete if `is_deleted = true`.
- **Error recovery**: the watermark moves only after a successful `MERGE`. If a load fails, the next run picks up the same rows and the `MERGE` makes repeating them safe. Snowflake calls retry 3 times (2s, 4s, 8s), Airflow retries each task twice, and a failure sends an email.
- **Summary table**: recomputed from all good data on every run and fully replaced, so it can never drift.

## Run it

```bash
pip install -r requirements.txt
pytest                                   # no Snowflake needed, uses an in-memory fake

# real run
export SNOWFLAKE_ACCOUNT=... SNOWFLAKE_USER=... SNOWFLAKE_PASSWORD=...
export SNOWFLAKE_DATABASE=HOSPITAL SNOWFLAKE_SCHEMA=ANALYTICS SNOWFLAKE_WAREHOUSE=COMPUTE_WH
# run sql/create_tables.sql in Snowflake once, then:
python -m etl.pipeline
```

Email alerts: set `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `ALERT_FROM`, `ALERT_TO`. Without them alerts are only logged.

Airflow: put the project on `PYTHONPATH`, copy or link `dags/hospital_etl_dag.py` into your dags folder, and make `ETL_STAGING_DIR` shared storage if tasks run on different workers.

