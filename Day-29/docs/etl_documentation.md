# ETL Documentation

## DAG: `orders_etl`
Daily, `catchup=False`, `max_active_runs=1`, retries=2 with exponential backoff. Linear flow:

`extract_transform → load_staging → merge_and_mart → validate_and_audit`

| Task | Code | What it does | Fails when |
|---|---|---|---|
| extract_transform | `pipeline.step_extract_transform` | Reads CSV (all text), checks required columns, cleans/types/validates, dedupes, derives amounts, runs pre-load DQ, writes `clean.parquet`, `rejects.csv`, `metrics.json` | file/columns missing; reject ratio > 20%; row reconciliation fails |
| load_staging | `step_load_staging` | Bulk loads clean rows into `RAW.ORDERS_STG` (`write_pandas`, Parquet + COPY) tagged with BATCH_ID | Snowflake connection/privilege error |
| merge_and_mart | `step_merge_and_mart` | `sql/02_merge_core.sql` (MERGE) then `sql/03_build_mart.sql` (rebuild only affected dates) | SQL error |
| validate_and_audit | `step_validate_and_audit` | Staged count, duplicates, nulls, CORE-vs-MART revenue; writes audit row | any DQ rule fails (audit row `DQ_FAILED`, task fails) |

## Transform rules (`etl/transform.py`)
1. Trim text; lower-case status; upper-case country; title-case category.
2. Coerce types (`errors="coerce"`), so bad values become nulls instead of crashing the run.
3. Validate; each rejected row gets one reason (see data dictionary).
4. Deduplicate on `order_id`, keep last.
5. Derive `gross_amount = quantity × unit_price`; `net_revenue = gross_amount` only for `completed`.
6. Defaults: country `UNKNOWN`, category `Uncategorized`, product `Unknown`.

## Idempotency & re-runs
- MERGE is keyed on `order_id` and updates only when a tracked field changed, so running the same batch twice yields the same CORE state (covered by `test_e2e_snowflake`).
- The mart refresh deletes and recomputes only dates present in the batch.
- `RAW.ORDERS_STG` is append-only; a replay adds another staged copy under a new BATCH_ID but does not duplicate CORE.

## Failure handling
| Situation | Behaviour |
|---|---|
| Transient Snowflake/network error | Airflow retries the task (2×, backoff) |
| Too many bad rows (>20%) | Run fails before loading; inspect `rejects.csv` |
| Post-load DQ failure | Task fails; `AUDIT.PIPELINE_RUNS.STATUS = DQ_FAILED` |
| Missing env var | `EnvironmentError` naming the variables |

## Code documentation
Every module has a docstring describing its role; non-obvious decisions (why Parquet hand-off, why `errors="coerce"`, why MERGE change detection) are commented where they occur. Tests double as executable specification of the rules above.
