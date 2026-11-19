# Demo Script (~8 minutes)

**Before you start:** `.env` filled, Snowflake objects created, `docker compose up -d` already running, Airflow UI open on :8080, Snowflake worksheet open, dashboard on :8501 (optional). Generate data with an obviously dirty file: `python scripts/generate_sample_data.py --rows 1000`.

| Time | Do | Say |
|---|---|---|
| 0:00 | Slide 1–2 | "This is a small orders pipeline: CSV to Snowflake, orchestrated by Airflow in Docker. I'll show the flow, the quality gates, and the results." |
| 1:00 | Show `data/raw/orders.csv` (open in editor) | "The file has real-world problems: duplicates, negative quantities, bad dates, messy casing." |
| 1:45 | Airflow UI → `orders_etl` → Graph view | "Four tasks, each retryable on its own. Credentials come from `.env`, never code." |
| 2:30 | Click **Trigger**, watch tasks turn green | "Transform validates and cleans first; bad rows never reach Snowflake." |
| 3:30 | Terminal: `cat data/processed/<batch>/metrics.json` and `head rejects.csv` | "1,020 rows in, rejects written with a reason each. clean + rejects always equals input." |
| 4:30 | Snowflake: `SELECT * FROM AUDIT.PIPELINE_RUNS ORDER BY STARTED_AT DESC LIMIT 3;` | "Every run is audited, including data-quality failures." |
| 5:00 | Snowflake: `SELECT ORDER_DATE, SUM(NET_REVENUE) FROM MART.DAILY_SALES GROUP BY 1 ORDER BY 1 LIMIT 10;` | "The mart is what the dashboard reads: small and pre-aggregated." |
| 5:45 | **Idempotency:** trigger the DAG again, then `SELECT COUNT(*) FROM CORE.ORDERS;` | "Same count: MERGE means re-runs don't create duplicates." |
| 6:30 | Dashboard in browser, change a filter | "Cached for 5 minutes and reads the mart, so filters are instant." |
| 7:15 | Slide: tests + optimisation | "35 automated tests; vectorising the transform gave 59×–234× speed-up on 100k rows." |
| 8:00 | Questions | |

## If something goes wrong
- **Task red:** open its log; say "this is exactly why tasks are separate: retry only this one." Click *Clear*.
- **Snowflake login fails:** switch to `python scripts/run_pipeline.py --dry-run` and show transform + rejects locally.
- **Dashboard blank:** run the DAG first; the mart is empty until it succeeds.

## Likely questions
- *Why MERGE, not truncate-and-load?* Idempotent and cheaper; only changed rows are written.
- *What if the file is 100× bigger?* Move ingestion to a stage + COPY / Snowpipe; transform stays vectorised; MERGE and incremental mart already scale with batch size.
- *How do you know data is right?* Pre-load rules, row reconciliation, post-load uniqueness/null checks, mart-vs-core revenue match.
