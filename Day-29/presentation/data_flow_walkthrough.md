# Data Flow Walkthrough

Follow one messy row through the pipeline.

**Input row (CSV):** `ORD0000042, C00007, Headphones, electronics, 2, 59.99, 2026-11-03, "  COMPLETED ", in`

| Stage | What happens | Row now |
|---|---|---|
| 1. Extract | Read as text; header normalised; required columns checked | all strings |
| 2. Transform | trim/case: status `completed`, country `IN`, category `Electronics`; types: qty 2, price 59.99, date 2026-11-03; validation passes; derive gross 119.98, net 119.98 | typed, clean |
| 3. Pre-load DQ | no dupes/nulls; clean + rejects = raw; rejects < 20% | approved |
| 4. Staging | `write_pandas` → `RAW.ORDERS_STG` with BATCH_ID | staged copy |
| 5. Merge | `MERGE` into `CORE.ORDERS` by `ORDER_ID` (insert new, update only if changed) | one row per order |
| 6. Mart | delete + recompute `MART.DAILY_SALES` for 2026-11-03 | counted in IN × Electronics × 2026-11-03 |
| 7. Validate | staged count, no duplicate/NULL keys, CORE revenue = MART revenue; audit row written | SUCCESS |

**A bad row** (`quantity = -1`) stops at stage 2: it is written to `rejects.csv` with reason `invalid_quantity` and never reaches Snowflake.

**A duplicate** `order_id` keeps the last occurrence; the earlier one is logged as `duplicate_order_id`.
