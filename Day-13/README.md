# Day 13 – Apache Airflow (Docker) → Apify API → your Postgres (pgAdmin)

Only **Airflow** runs in Docker. The ETL calls the **Apify API**, transforms the data and loads it into **your local Postgres**, which you view in **your pgAdmin app**.

```
day13-airflow/
├── docker-compose.yml          # one service: airflow
├── .env                        # Postgres + Apify settings (keep private)
├── .env.example                # same file without secrets
├── plugins/hello_operator.py   # custom operator
└── dags/
    ├── 01_basic_operators.py       # BashOperator, PythonOperator, custom operator
    ├── 02_postgres_operator.py     # SQL (Postgres) operator
    ├── 03_apify_etl_pipeline.py    # ETL: Apify -> Postgres, quality check
    └── 04_advanced_features.py     # XCom, branching, trigger rules, task group
```

## 1. Setup
**Postgres (pgAdmin, once):** right-click *Databases → Create → Database* → `warehouse`.
**`.env`:** set `PG_USER`, `PG_PASSWORD`, `APIFY_TOKEN`.

```bash
docker compose up -d
docker compose logs -f airflow      # wait ~1 min until the webserver is up
```
Open http://localhost:8080 → `admin` / `admin`.

How this maps to the "Airflow setup" tasks:
| Task | In this project |
|---|---|
| `pip install apache-airflow` | already inside the `apache/airflow` Docker image |
| Initialize database | `airflow db migrate` (runs on start, SQLite in `airflow_db/`) |
| Start webserver + scheduler | `airflow scheduler &` and `airflow webserver` (in the compose command) |
| Understand UI | section 4 |

After changing `.env`: `docker compose up -d --force-recreate`.

## 2. Run the ETL
1. Un-pause **03_apify_etl_pipeline** → ▶ **Trigger DAG** (the Apify actor takes ~1 min).
2. pgAdmin → `warehouse → Schemas → public → Tables` → Refresh.
3. Query:
```sql
SELECT * FROM apify_pages;
```

## 3. How data flows
```
Apify API (website-content-crawler)
   │  extract   : POST run-sync-get-dataset-items  -> raw JSON items
   │  transform : url, title, word_count, preview, crawled_at
   │  quality   : not empty / url present / no duplicates
   │  load      : upsert (PostgresHook)
   ▼
Your Postgres  warehouse.apify_pages  ──►  pgAdmin
```
`create_table` runs first. Tasks pass data to each other with **XCom**. `finish` has trigger rule `all_done`, so it always runs.

To crawl something else, edit `ACTOR_ID` / `RUN_INPUT` at the top of `dags/03_apify_etl_pipeline.py` (the transform expects `url`, `text`, `metadata.title`, `crawl.loadedTime`; adjust it for other actors).

## 4. Airflow UI guide
- **DAGs** – list, on/off toggle, schedule, last run.
- **Grid** – run history; green = success, red = failed.
- **Graph** – task dependencies.
- **Task → Logs / XCom** – logs and data passed between tasks.
- **Admin → Connections** – `warehouse_db` (built from `.env`).

## 5. Concepts
| Concept | Meaning |
|---|---|
| DAG | Workflow = tasks + order, no loops |
| Operator / Task | Template (`BashOperator`, `PythonOperator`, SQL, custom) / one instance of it |
| Dependency | `a >> b` → b runs after a |
| Execution date | The date a run represents (`{{ ds }}`) |
| Scheduler | Starts runs on schedule |
| XCom | Small data passed between tasks |
| Trigger rule | When a task runs based on upstream results |

## 6. DAGs
| DAG | Schedule | Topics |
|---|---|---|
| 01_basic_operators | `@daily` | BashOperator, PythonOperator, custom operator, dependencies |
| 02_postgres_operator | `@hourly` | SQL operator (successor of `PostgresOperator`), `{{ ds }}` |
| 03_apify_etl_pipeline | `0 6 * * *` | Extract / Transform / Load, data quality check, XCom, retries, trigger rule |
| 04_advanced_features | `@weekly` | XCom, branching, trigger rules, task group |

Test a DAG without the scheduler:
```bash
docker compose exec airflow airflow dags test 03_apify_etl_pipeline 2024-01-01
```

## 7. Troubleshooting
| Problem | Fix |
|---|---|
| `extract` fails with 401 | Wrong/expired `APIFY_TOKEN`; update `.env` and recreate the container. |
| `extract` fails with 402/403 | Apify credits/permissions; check your Apify plan. |
| Postgres `connection refused` | Allow Docker to connect: `listen_addresses = '*'` in `postgresql.conf` and a `host all all 0.0.0.0/0 scram-sha-256` line in `pg_hba.conf`, restart Postgres (local learning only). |
| `database "warehouse" does not exist` | Create it in pgAdmin or change `PG_DB`. |
| DAG not visible | `docker compose exec airflow airflow dags list-import-errors` |

## Security
`.env` holds secrets – it is in `.gitignore`; never commit it. Regenerate the Apify token if it was shared.

## Deliverables
- [x] Airflow installed (Docker)
- [x] 4 DAGs
- [x] ETL pipeline as DAG (Apify → Postgres)
- [x] Scheduled workflows
- [x] README
