# Day 24 – Data Warehouse on Snowflake (Retail Sales Star Schema)

## Run
```bash
pip install -r requirements.txt
cp .env.example .env        # fill in your Snowflake credentials
python run_pipeline.py              # build + load + validate
python run_pipeline.py --scd-demo   # change source customers, reload, show SCD2 history
```
Each run is re-runnable: dims use MERGE / SCD2 logic, facts load only new `sale_id`s.

## Architecture
`STG` (raw/dirty source) -> `DW` (dimensional model) in database `DW_DAY24`.

```
dim_date ─┐
dim_customer (SCD2) ─┤
dim_product (SCD1) ──┼── fact_sales (grain: one order line)
dim_store (SCD1) ────┘
```

| Table | Type | Notes |
|---|---|---|
| dim_date | Static | 2020-2030, ISO week, month/quarter/year hierarchy, fiscal year (Apr start), weekend + holiday flags |
| dim_customer | SCD Type 2 | tracks `city`, `segment` via MD5 `row_hash`; `effective_date`/`end_date`(exclusive)/`is_current` |
| dim_product | SCD Type 1 | overwrite on change |
| dim_store | SCD Type 1 | overwrite on change |
| fact_sales | Transaction fact | additive measures: quantity, gross, discount, net, cost, profit |

Hierarchies: Date → Week/Month → Quarter → Year (and Fiscal). Product: Category → Product. Store: Region → City → Store. Customer: Segment, City.

## Load logic
- **Dimensions:** trim / INITCAP / LOWER email / NULL→"Unknown"; dedupe with `QUALIFY ROW_NUMBER()`. Unknown member key `-1` in each dim.
- **SCD2:** (1) close current rows whose hash changed, (2) insert new customers and new versions. First version starts `1900-01-01` so historical facts resolve.
- **Facts:** point-in-time customer lookup (`order_date BETWEEN effective_date AND end_date`), product/store lookup, orphans mapped to `-1`, rows with `quantity <= 0` rejected, measures calculated (gross, discount, net, cost, profit).

## Constraints and "indexes" in Snowflake
PK/FK/UNIQUE are declared (informational, `RELY`) but **not enforced** – so integrity is proven by the validation checks. Snowflake has no indexes; `fact_sales` uses `CLUSTER BY (date_key)`.

## Validation (`06_validation.sql` → `DW.validation_results`)
Count reconciliation (staging vs dims/fact, sum of quantity), referential integrity (4 FK orphan checks), data quality (duplicates, one current SCD2 row per customer, no overlapping versions, NULL measures, net = gross − discount, clean emails). Fact rows mapped to Unknown customer is a **WARN** (sample data intentionally contains ~1% orphan customer `C9999`).

## Known limitations
Holidays are fixed-date only (movable holidays like Diwali need a calendar source). Source data is synthetic; swap `02_staging_sample_data.sql` for your real extract/COPY INTO.

## Validation results
Paste the output of `python run_pipeline.py` here after your run.
