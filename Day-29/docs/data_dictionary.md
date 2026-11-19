# Data Dictionary

## Source file: `data/raw/orders.csv`
All columns arrive as text and are typed in the transform step.

| Column | Meaning | Rule |
|---|---|---|
| order_id | Unique order key | required, trimmed; duplicates → last wins |
| customer_id | Customer key | required |
| product | Product name | optional → `Unknown` |
| category | Product category | optional → `Uncategorized`; title-cased |
| quantity | Units ordered | integer > 0 |
| unit_price | Price per unit | number ≥ 0 (0 allowed), rounded to 2 dp |
| order_date | Order date | parseable date |
| status | Order state | one of `completed, pending, cancelled, refunded` (case/space insensitive) |
| country | ISO-style country code | upper-cased; missing → `UNKNOWN` |

## RAW.ORDERS_STG
Same business columns as CORE.ORDERS plus:

| Column | Type | Meaning |
|---|---|---|
| GROSS_AMOUNT | NUMBER(14,2) | quantity × unit_price |
| NET_REVENUE | NUMBER(14,2) | gross_amount if status = completed, else 0 |
| BATCH_ID | VARCHAR | pipeline batch that loaded the row |
| LOADED_AT | TIMESTAMP_NTZ | load time |

## CORE.ORDERS (PK: ORDER_ID, clustered by ORDER_DATE)

| Column | Type | Null? | Meaning |
|---|---|---|---|
| ORDER_ID | VARCHAR | no | business key |
| CUSTOMER_ID | VARCHAR | no | |
| PRODUCT | VARCHAR | yes | |
| CATEGORY | VARCHAR | yes | |
| QUANTITY | NUMBER(10,0) | yes | |
| UNIT_PRICE | NUMBER(12,2) | yes | |
| ORDER_DATE | DATE | no | |
| STATUS | VARCHAR | yes | |
| COUNTRY | VARCHAR | yes | |
| GROSS_AMOUNT | NUMBER(14,2) | yes | |
| NET_REVENUE | NUMBER(14,2) | yes | revenue recognised only for completed orders |
| LAST_BATCH_ID | VARCHAR | yes | last batch that inserted/changed the row |
| UPDATED_AT | TIMESTAMP_NTZ | yes | last change time |

Note: Snowflake does not enforce PRIMARY KEY; uniqueness is guaranteed by MERGE and verified by the post-load DQ check.

## MART.DAILY_SALES (grain: ORDER_DATE × COUNTRY × CATEGORY)

| Column | Meaning |
|---|---|
| ORDERS | number of orders (all statuses) |
| UNITS | sum of quantity |
| GROSS_AMOUNT | sum of gross amount |
| NET_REVENUE | sum of net revenue |
| CANCELLED_ORDERS | orders with status `cancelled` |
| REFRESHED_AT | last refresh |

## AUDIT.PIPELINE_RUNS

| Column | Meaning |
|---|---|
| BATCH_ID, STARTED_AT, FINISHED_AT | run identity and timing |
| RAW_ROWS / CLEAN_ROWS / REJECT_ROWS | row accounting (`clean + reject = raw`) |
| STATUS | `SUCCESS` or `DQ_FAILED` |

## Reject reasons (`data/processed/<batch>/rejects.csv`)
`missing_order_id`, `missing_customer_id`, `invalid_quantity`, `invalid_unit_price`, `invalid_order_date`, `invalid_status`, `duplicate_order_id`. First failing rule wins, in that order (duplicates are checked last).
