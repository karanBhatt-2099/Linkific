# Day 21 – Multi-Source Data Collection Pipeline

Collects data from **10 extractions across 6 source types**, handles several file formats,
integrates everything (schema mapping → key matching → merge → conflict handling → lineage)
and loads it into **Snowflake**. Orchestrated with **Airflow in Docker**.

```
 APIs (3) ─────────┐
 PostgreSQL ───────┤
 MongoDB ──────────┤                          ┌─> Snowflake  RAW.*        (as collected)
 CSV/JSON/Excel ───┼─> data/raw/*.parquet ─┬──┤
 Web scraping ─────┤                       │  └─> Snowflake  ANALYTICS.*  (integrated)
 SFTP (XML) ───────┘                       └─> data/converted/ (csv/json/parquet/avro)
```

## Project layout

| Path | Purpose |
|---|---|
| `.env` | **All config + Snowflake credentials** |
| `docker-compose.yml`, `Dockerfile` | Airflow + source systems (Postgres, MongoDB, SFTP) |
| `dags/multi_source_pipeline.py` | The Airflow DAG (scheduling, retries, order of tasks) |
| `src/extract_api.py` | 3 APIs: JSONPlaceholder, Open-Meteo, REST Countries |
| `src/extract_db.py` | PostgreSQL + MongoDB |
| `src/extract_files.py` | CSV, JSON, Excel |
| `src/extract_scrape.py` | Web scraping (books.toscrape.com) |
| `src/extract_sftp.py` | SFTP download + XML parse |
| `src/formats.py` | JSON/XML/Parquet/Avro readers + writers + demo |
| `src/integrate.py` | Schema mapping, merge, conflicts, lineage |
| `src/load_snowflake.py` | Snowflake loader |
| `init/` | Seed data for Postgres and MongoDB |
| `data/files/`, `sftp_data/` | Sample CSV/JSON/Excel and the XML served by SFTP |

## Quick start

### 1. Snowflake setup (once)
Run in a Snowflake worksheet (names must match `.env`):
```sql
CREATE DATABASE IF NOT EXISTS DAY21_DB;
-- warehouse COMPUTE_WH usually exists already; schemas RAW and ANALYTICS are created by the pipeline
```

### 2. Edit `.env`
Fill in `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD` (+ role/warehouse if different).
Account format: `orgname-accountname` (Snowsight → account menu → *Copy account identifier*).
Leave the other values as they are – they point to the Docker services.

### 3. Start everything
```bash
chmod -R 777 data logs            # Linux/Mac: lets the Airflow container write here
docker compose build
docker compose up -d
```
Open **http://localhost:8080** (login `admin` / `admin`).

### 4. Run the pipeline
Un-pause the DAG **`day21_multi_source_pipeline`** and click ▶ *Trigger DAG*.
It also runs automatically every day at 06:00 (`schedule="0 6 * * *"`).

### 5. Check the result in Snowflake
```sql
SELECT * FROM DAY21_DB.ANALYTICS.CUSTOMERS_GOLD;
SELECT * FROM DAY21_DB.ANALYTICS.CUSTOMER_CONFLICTS;
SELECT * FROM DAY21_DB.ANALYTICS.ORDERS_GOLD;
SELECT * FROM DAY21_DB.ANALYTICS.DATA_LINEAGE;
SHOW TABLES IN DAY21_DB.RAW;          -- one table per extracted source
```

## DAG tasks

```
extract_api_users ─┐
extract_api_weather│
extract_api_countries
extract_postgres   │
extract_mongodb    ├─> convert_formats -> load_raw_to_snowflake -> integrate_to_warehouse
extract_files_csv  │
extract_files_json │
extract_files_excel│
extract_web_scrape │
extract_sftp_xml  ─┘
```
All 10 extract tasks run in parallel. Each saves a parquet file to `data/raw/`
with two lineage columns: `_source` and `_ingested_at`.

## Sources covered

| Requirement | What is used |
|---|---|
| APIs (3+) | JSONPlaceholder, Open-Meteo, REST Countries |
| Databases (2+ types) | PostgreSQL (relational), MongoDB (document) |
| Files | CSV, JSON, Excel (`.xlsx`) |
| Web scraping | `requests` + BeautifulSoup |
| SFTP | `paramiko` against an `atmoz/sftp` container |

## Format handling (`src/formats.py`)

| Task | Function |
|---|---|
| JSON → DataFrame | `json_to_df()` (`pd.json_normalize`, flattens nested JSON) |
| XML parsing | `xml_to_df()` (`xml.etree`) |
| Parquet | `df.to_parquet()` / `parquet_to_df()` |
| Avro | `df_to_avro()` / `avro_to_df()` (`fastavro`) |
| Any → all formats | `convert_all(df, name)` writes csv + json + parquet + avro |

Try the demo (inside the container):
```bash
docker compose exec airflow-scheduler python -m src.formats
ls data/converted
```
The DAG's `convert_formats` task also converts `api_users`, `sftp_customers` and `pg_orders` into all 4 formats.

## Integration rules (`src/integrate.py`)

**Schema mapping** – every customer source uses different column names, e.g. CSV has
`full_name`, others have `name`. `MAPPINGS` renames each source to one unified schema:
`email, name, phone, city, loyalty_tier, updated_at`.

**Key matching** – `email` (lower-cased and trimmed) is the key across customer sources.
For orders, Postgres only has `customer_id`, so it is joined to `pg_customers` to obtain the email.

**Merge strategy** – *source priority with gap filling*. Priority order is the order of `MAPPINGS`:
`pg_customers > sftp_customers > csv_customers > api_users`. For each email, the highest-priority
non-null value wins; missing values are filled from lower-priority sources.
Orders are de-duplicated on `order_id` (Postgres wins over the JSON file).

**Conflict handling** – when sources disagree (e.g. Leanne's city is Mumbai / Pune / Gwenborough),
the winner is chosen by priority and **every disagreement is stored** in `CUSTOMER_CONFLICTS`
(`all_values`, `chosen_value`) so nothing is silently lost.

**Data lineage**
- Row level: `_source`, `_ingested_at` in every RAW table; `SOURCES` column in `CUSTOMERS_GOLD`
  lists every system that contributed to the row.
- Table level: `DATA_LINEAGE` records target table, source, rows in, and run timestamp.

## Error handling, logging, scheduling

- **Retries**: every task retries 2× with a 2 minute delay (`default_args`).
- **Failure callback**: `on_failure()` logs the failed task id and exception.
- **HTTP errors**: `raise_for_status()` turns bad API/scrape responses into task failures.
- **Connections**: DB and SFTP connections are closed in `finally` blocks.
- **Logging**: Python `logging` in every module; view per task in Airflow UI → task → *Logs*.
- **Scheduling**: cron in the DAG (`0 6 * * *`); `catchup=False`.

## Useful commands

```bash
docker compose logs -f airflow-scheduler       # follow logs
docker compose exec airflow-scheduler airflow tasks test day21_multi_source_pipeline extract_postgres 2025-01-01
docker compose down                            # stop
docker compose down -v                         # stop and delete DB volumes
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `Permission denied` writing to `data/` or `logs/` | `chmod -R 777 data logs` |
| Snowflake `250001` / login error | Check `SNOWFLAKE_ACCOUNT` format, user, password, role |
| `Database 'DAY21_DB' does not exist` | Create it (step 1) or change `SNOWFLAKE_DATABASE` |
| SFTP task fails | `docker compose logs sftp`; make sure `sftp_data/customers.xml` exists |
| Postgres/Mongo seed not applied | Seeds run only on first start: `docker compose down -v && docker compose up -d` |
| Scrape/API task fails | Check internet access from Docker; the task will retry automatically |
| `pip` dependency conflict during `docker compose build` | Pin the conflicting package in `requirements.txt` |
| Changed `.env` but no effect | `docker compose up -d --force-recreate` |

## Extending
- New source: add a function in `src/extract_*.py` that ends with `save_raw(df, "name", "source")`, add it to `EXTRACTS` in the DAG.
- New customer source: add a `MAPPINGS` entry in `integrate.py`; its position sets its priority.
