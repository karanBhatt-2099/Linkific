# Day 26 - Airflow ETL Pipeline (Docker)

## Run it
```bash
mkdir -p data logs dags
chmod -R 777 data logs      # Linux only, lets the container write
docker compose up -d
```
Open http://localhost:8080 (login `admin` / `admin`), unpause **day26_etl_pipeline**, click **Trigger**.

Test one run from the terminal:
```bash
docker compose exec airflow airflow dags test day26_etl_pipeline 2026-11-16
```
Stop: `docker compose down`

## DAG structure
```
start -> extract_sales     -> transform_sales     -> load_sales     \
      -> extract_customers -> transform_customers -> load_customers -> quality_check -> end
```
| Task | What it does |
|---|---|
| extract_sales / extract_customers | Write raw CSVs to `data/` |
| transform_sales | Splits good rows and bad rows (bad rows go to the dead letter file) |
| transform_customers | Trims and title-cases names |
| load_sales / load_customers | Load into SQLite `data/warehouse.db` (re-runs are safe) |
| quality_check | Fails and alerts if nothing loaded or more than 20% of rows are bad |

## Schedule
`0 6 * * *` = daily at 06:00. `catchup=False`, `max_active_runs=1`.

## Monitoring
- **Task success/failure alerts:** `on_failure_callback` writes to `data/alerts.log`.
- **Data quality alerts:** `quality_check` writes `DATA QUALITY: ...` to `data/alerts.log` and fails the task.
- **Performance:** `on_success_callback` logs `PERF: <task> finished in Xs` (see task logs; Gantt view in the UI).
- **Logging:** all tasks use Python `logging`; view in UI > task > Logs, or in `logs/`.

## Failure handling
- **Retries:** 2 retries, 1 min delay with exponential backoff, 5 min timeout per task.
- **Failure callback:** logs and writes the alert after the final failure.
- **Dead letter:** bad rows are saved to `data/dead_letter_<date>.csv`, not lost, and the pipeline continues.

## Optimization
- **Parallel execution:** sales and customers branches run at the same time (LocalExecutor).
- **Resource allocation:** `max_active_tasks=4` (DAG), `parallelism=8` (Airflow), `max_active_runs=1`.
- **Tuning:** simple stdlib code, no heavy dependencies; loads are idempotent so retries are cheap.

## Demo failure
The sample data contains 2 bad rows out of 20 (10%), so it passes. Edit `MAX_BAD_RATIO` to `0.05` in the DAG and re-trigger to see `quality_check` fail and write an alert.
