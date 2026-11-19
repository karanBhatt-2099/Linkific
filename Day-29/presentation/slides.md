---
marp: true
theme: default
paginate: true
---

# Orders ETL Pipeline
Snowflake · Airflow (Docker) · Python
*Final project presentation*

---

# Problem & goal
- Daily orders arrive as CSV with real-world quality issues
- Goal: trustworthy, repeatable load into Snowflake for analytics
- Constraints: small, cheap, credentials never in code

---

# Architecture
```
orders.csv → extract/transform → RAW.ORDERS_STG → CORE.ORDERS (MERGE) → MART.DAILY_SALES → Dashboard
                    ↑ Airflow DAG in Docker, credentials from .env ↑
```
- 4 independent Airflow tasks, retries with backoff
- Snowflake layers: RAW → CORE → MART (+ AUDIT)

---

# Data flow
1. Extract and validate schema
2. Clean, type, dedupe, derive revenue
3. Bad rows → `rejects.csv` with reason
4. Bulk load → MERGE → incremental mart
5. Post-load checks + audit record

---

# Data quality
- 7 reject reasons, every row accounted for
- Pre-load gate: > 20% rejects fails the run
- Post-load: staged count, no duplicate/NULL keys, CORE = MART revenue
- Audit table per run (`SUCCESS` / `DQ_FAILED`)

---

# Live demo
Airflow trigger → rejects → audit → mart → re-run (idempotent) → dashboard

---

# Testing
- 37 tests: 35 passed locally, 2 need Snowflake/Airflow (run on your side)
- Edge cases (26), data quality (5), performance (2), end-to-end (4)
- Passes on pandas 2.2 and 3.0

---

# Optimization
| Area | Change | Result |
|---|---|---|
| Code | vectorised transform | **59×–234× faster** on 100k rows (measured) |
| Queries | batch-scoped MERGE, change detection, incremental mart | cost scales with batch, not history |
| Pipeline | separate retryable tasks, XSMALL warehouse, 60 s auto-suspend | pay only while running |
| Dashboard | reads mart + 5-min cache + result cache | fast filters |

---

# Lessons & next steps
- Validate before load; reconcile after load
- Idempotent writes make re-runs safe
- Next: key-pair auth, Snowpipe ingestion, dbt for SQL layer, alerting on DQ failure

---

# Questions?
