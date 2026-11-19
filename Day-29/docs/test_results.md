# Test Results

Run date: 2026-11-19 · Environment: Linux sandbox, Python 3.13, `python -m pytest`

## Summary
| Environment | Passed | Skipped | Failed |
|---|---|---|---|
| pandas 3.0.5 | 35 | 2 | 0 |
| pandas 2.2.3 (closest to the Airflow image's pandas 2.x) | 35 | 2 | 0 |

## What was and was not run

| Area | Tests | Status |
|---|---|---|
| End-to-end (local: CSV → extract → transform → DQ → Parquet; deterministic re-run) | 2 | ✅ passed |
| End-to-end (Snowflake: full run, twice, asserts idempotent MERGE and unchanged revenue) | 1 | ⏭ **skipped, not run** – no Snowflake credentials in the test sandbox |
| DAG integrity (imports, 4 expected tasks, catchup off, max_active_runs=1) | 1 | ⏭ **skipped, not run** – Airflow 2.9.3 does not support the sandbox's Python 3.13. Only a static check was done: the DAG file compiles and defines the 4 tasks |
| Edge cases (26 tests: zero/negative/fractional/non-numeric quantity, bad price, bad/missing date, unknown status, missing keys, whitespace-only id, duplicates keep-last, zero price allowed, defaulted optional fields, unicode, empty input, missing file, missing columns, header case) | 26 | ✅ passed |
| Data quality (reject ratio gate, nothing-valid, row-loss detection, duplicate keys, reconciliation on sample data) | 5 | ✅ passed |
| Performance (transform) | 2 | ✅ passed |

## Performance (transform step, measured)
| Rows | pandas 3.0.5 | pandas 2.2.3 |
|---|---|---|
| 10,200 | 0.04 s | 0.05 s |
| 102,000 | 0.16 s | 0.47 s |

Before/after optimisation on 102k rows (`scripts/benchmark_transform.py`, outputs identical at 96,000 clean rows):

| Version | pandas 3.0.5 | pandas 2.2.3 |
|---|---|---|
| naive row-by-row | 39.6 s | 29.1 s |
| vectorised (shipped) | 0.17 s | 0.49 s |

## Defects found while testing
- `datetime.utcnow()` deprecation warnings → replaced with timezone-aware `_utcnow()`.
- Removed a redundant, always-true check in `quality.check_dataframe`.

## Still to do on your side (needs your accounts/Docker)
1. Fill `.env`, run `python scripts/setup_snowflake.py`.
2. `python -m pytest` again with credentials → runs `test_e2e_snowflake`.
3. `docker compose up --build`, trigger `orders_etl`, confirm 4 green tasks (this also exercises the DAG for real).
4. `python scripts/benchmark_snowflake.py` twice for Snowflake/dashboard timings.
5. Record results in the table below.

| Check | Result | Date |
|---|---|---|
| Docker Airflow run, all tasks green | _pending_ | |
| Snowflake e2e test | _pending_ | |
| Dashboard query timings (cold / cached) | _pending_ | |
