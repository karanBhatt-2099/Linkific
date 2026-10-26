# ETL Pipeline: PostgreSQL + REST API + CSV → Snowflake

A small, complete ETL pipeline that runs locally in VS Code and loads a sales warehouse in Snowflake.
PostgreSQL is managed through **pgAdmin**.

## Architecture

Diagram: [`docs/architecture.drawio`](docs/architecture.drawio) (open at https://app.diagrams.net or with the draw.io VS Code extension).

```
PostgreSQL (customers, orders) ─┐
REST API (products, paginated) ─┼─> Extract ─> Staging (Parquet) ─> Transform (pandas) ─> Load ─> Snowflake
CSV file (order_items)         ─┘                                                            STAGING / ANALYTICS
        Orchestration: Airflow DAG      Error handling: logging, retry, email alerts
```

| Layer | What it does | Code |
|---|---|---|
| Sources | PostgreSQL `customers`, `orders`; dummyjson API `products`; CSV `order_items` | `sql/`, `data/source/` |
| Extract | One extractor per source type; API pagination; incremental DB extract | `src/extract/` |
| Staging | Raw extracts saved as Parquet in `data/staging/` | `src/staging.py` |
| Transform | Cleaning, type conversion, joins, business rules | `src/transform/transformations.py` |
| Load | Upsert (MERGE) and truncate-and-load into Snowflake | `src/load/snowflake_loader.py` |
| Orchestration | Airflow DAG (Docker) runs Extract → Transform → Load; `main.py` runs the same steps without Airflow | `dags/etl_dag.py`, `src/pipeline.py` |
| Error handling | `try/except`, log file, retry with backoff, email alert | `src/utils/` |

## What gets built in Snowflake

| Table | Load strategy |
|---|---|
| `ANALYTICS.DIM_PRODUCTS` | Truncate and load (full refresh each run) |
| `ANALYTICS.DIM_CUSTOMERS` | Upsert (MERGE on `customer_id`) |
| `ANALYTICS.FACT_SALES` | Incremental upsert (MERGE on `order_item_id`), driven by `orders.updated_at` watermark |
| `ANALYTICS.AGG_DAILY_SALES` | Rebuilt from the fact table after each load (daily orders, units, revenue; cancelled excluded) |
| `STAGING.STG_*` | Temporary landing tables used as the MERGE source |

## Transformations

- **Cleaning:** trim whitespace, fix case (names, emails, cities, statuses), fill missing brand/discount, drop duplicate rows.
- **Type conversion:** text → numbers/dates, API prices → decimals.
- **Rejected data (logged):** blank/invalid quantity, unknown product id, order items whose order does not exist.
- **Join:** `order_items` (CSV) + `orders` + `customers` (PostgreSQL) + `products` (API).
- **Business logic:** `gross_amount`, `discount_amount`, `net_amount`, and `order_value_tier` (HIGH ≥ 500, MEDIUM ≥ 100, else LOW).

## Setup

1. **Python environment (VS Code terminal)**
   ```
   python -m venv .venv
   .venv\Scripts\activate          # Windows   (Mac/Linux: source .venv/bin/activate)
   pip install -r requirements.txt
   ```
2. **PostgreSQL in pgAdmin**
   - Create a database named `etl_source`.
   - Open Query Tool on it and run `sql/postgres_setup.sql`.
3. **Snowflake**
   - Use a trial/any account. The pipeline creates the database `ETL_DEMO`, the schemas and the tables by itself (`sql/snowflake_setup.sql`).
4. **Config**
   - Copy `.env.example` to `.env` and fill in your pgAdmin/Postgres password and Snowflake credentials.

## Run with Airflow (Docker)

Airflow runs in Docker and orchestrates the whole pipeline. PostgreSQL (pgAdmin) and your project stay on your machine.

```
docker compose build
docker compose up airflow-init        # one time: creates Airflow metadata DB and the admin user
docker compose up -d                  # starts webserver + scheduler
```

1. Open http://localhost:8080 and log in with `admin` / `admin`.
2. Unpause the DAG `etl_postgres_api_csv_to_snowflake` and click **Trigger DAG** (it also runs `@daily`).
3. To reload everything, use **Trigger DAG w/ config** and set `full_refresh` to true.

DAG graph:

```
extract_customers ─┐
extract_orders ────┤
extract_order_items┼─> transform ─> load_to_snowflake
extract_products ──┘
```

- The four extract tasks run in parallel, then `transform`, then `load_to_snowflake`.
- Tasks pass data through the staging Parquet files in `data/staging/` (the project folder is mounted into the container).
- Each task retries twice (2 min apart) on top of the in-code retries, and a failure triggers the email alert.
- `max_active_runs=1` prevents two runs from sharing the staging folder and watermark at once.
- Inside Docker, the Postgres host is set to `host.docker.internal` automatically, so keep `PG_HOST=localhost` in `.env` for local runs.
- If Airflow cannot reach Postgres, check that pgAdmin's server accepts connections from Docker (`listen_addresses` and `pg_hba.conf`).
- Linux: add `AIRFLOW_UID=$(id -u)` to `.env` before starting.
- Stop with `docker compose down` (add `-v` to also delete the Airflow metadata).

## Run without Docker

```
python main.py            # incremental run
python main.py --full     # ignore the watermark and reload everything
```

### See the incremental load work

1. Run `python main.py` (loads all 12 orders).
2. In pgAdmin run `sql/postgres_simulate_changes.sql` (updates order 1005, adds 1013 and 1014).
3. Run `python main.py` again. The log shows only 3 orders extracted, and Snowflake gets 1 updated and 2 new orders without duplicates.

Check results in Snowflake:
```sql
SELECT * FROM ETL_DEMO.ANALYTICS.FACT_SALES ORDER BY ORDER_ID;
SELECT * FROM ETL_DEMO.ANALYTICS.AGG_DAILY_SALES;
```

## Error handling

- Every extract and load call is wrapped in `@retry` (3 attempts, exponential backoff).
- All steps log to the console and `logs/etl.log`.
- Any failure stops the run, logs the stack trace, and sends an email if `ALERT_EMAIL_ENABLED=true` in `.env`.
- The watermark moves only after a fully successful load, so a failed run is safely re-run.

## Scope notes

- Batch ETL (transform before load), not ELT and not streaming.
- Change detection is timestamp-based (`updated_at` watermark), not log-based CDC.
- Customers are extracted in full each run so the fact join always has every customer.
- Airflow uses LocalExecutor in Docker Compose, which is right for local development, not a production deployment.

## Folder structure

```
etl_project/
├── main.py                 run everything in one process
├── Dockerfile              Airflow image + project dependencies
├── docker-compose.yml      Airflow webserver, scheduler, metadata DB
├── dags/etl_dag.py         Airflow DAG
├── requirements.txt
├── requirements-airflow.txt
├── .env.example
├── README.md
├── docs/architecture.drawio
├── sql/                 postgres_setup.sql, postgres_simulate_changes.sql, snowflake_setup.sql
├── data/source/         order_items.csv
├── data/staging/        Parquet files written at run time
├── logs/  state/        etl.log, watermark.json written at run time
└── src/
    ├── config.py, staging.py, pipeline.py
    ├── extract/         db_extractor.py, api_extractor.py, file_extractor.py
    ├── transform/       transformations.py
    ├── load/            snowflake_loader.py
    └── utils/           logger.py, retry.py, alerts.py, state.py
```
