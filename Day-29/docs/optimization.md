# Optimization Report

Measured numbers are marked **(measured)**; things that depend on your Snowflake account are marked **(to measure)** with the script that measures them.

## 1. Code optimization
| Change | Why | Result |
|---|---|---|
| Vectorised pandas transform instead of row-by-row loop | Python loops over rows are the classic ETL bottleneck | 100k rows: naive 29–40 s → vectorised 0.17–0.49 s, **59×–234×** faster, identical output (96,000 clean rows) **(measured, `scripts/benchmark_transform.py`, pandas 2.2.3 and 3.0.5)** |
| Read CSV as strings once, coerce types in bulk | avoids per-row parsing errors, one pass | included above |
| Parquet hand-off between tasks | typed, compressed, fast to read | n/a |
| Bulk load with `write_pandas` (Parquet + COPY) | row-wise INSERTs are orders of magnitude slower in Snowflake | **(to measure)** |

## 2. Query tuning (Snowflake)
| Technique | Where | Effect |
|---|---|---|
| MERGE only the current batch (`WHERE BATCH_ID = ...`) | `02_merge_core.sql` | scans the batch, not history |
| Change detection in `WHEN MATCHED AND (...)` | same | unchanged rows are not rewritten → less micro-partition churn |
| `CLUSTER BY (ORDER_DATE)` on CORE.ORDERS | `01_setup.sql` | partition pruning for date-filtered mart refresh. Benefit appears at larger volumes; at demo size it is neutral |
| Incremental mart (delete+insert affected dates) | `03_build_mart.sql` | cost proportional to the batch, not full history |
| Narrow column lists, no `SELECT *` on large tables | dashboard, mart | less data scanned |

Verify with Snowflake's Query Profile or `ACCOUNT_USAGE.QUERY_HISTORY` (look at partitions scanned vs total).

## 3. Pipeline performance
- Four small tasks so a failure retries only the failed step (no re-extract after a load error).
- `max_active_runs=1` prevents overlapping MERGEs on the same tables.
- Pre-load validation fails fast, before any warehouse time is spent.
- Warehouse `XSMALL`, `AUTO_SUSPEND=60`, `AUTO_RESUME=TRUE`: pay only while the pipeline runs.
- Transform throughput **(measured)**: ~190k–630k rows/s depending on pandas version (`tests/test_performance.py`).

## 4. Dashboard load time
| Technique | Effect |
|---|---|
| Dashboard reads `MART.DAILY_SALES` (pre-aggregated, one row per date×country×category) instead of CORE | scans orders of magnitude fewer rows |
| `st.cache_data(ttl=300)` | repeat page loads/filter changes don't hit Snowflake for 5 min |
| Snowflake result cache | identical queries within 24 h are served without warehouse compute |
| Filtering done in pandas on the cached mart | interactive filters cost no queries |

Measure on your account: `python scripts/benchmark_snowflake.py` twice (cold vs cached). Results append to `docs/benchmark_results.csv`. **(to measure)**

## Further options (not implemented, out of scope for a small pipeline)
Snowpipe/COPY from a stage for file ingestion, key-pair auth, dbt for the SQL layer, Airflow `SnowflakeOperator` + connections instead of env vars, dynamic tables for the mart.
