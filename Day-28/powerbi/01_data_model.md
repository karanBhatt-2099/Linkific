# Power BI Data Model

## 1. Connect to the warehouse
`Home → Get Data → Text/CSV` and load all 4 files from `data/`:
`fact_sales.csv`, `dim_date.csv`, `dim_product.csv`, `dim_customer.csv`

(For a real warehouse use `Get Data → SQL Server / PostgreSQL / Snowflake`, choose **Import** mode.)

## 2. Star schema relationships (Model view)

```
dim_date ──────┐
               │ 1
dim_product ───┼──< fact_sales
               │ *
dim_customer ──┘
```

| From (one side)           | To (many side)          | Cardinality | Filter direction |
|---------------------------|-------------------------|-------------|------------------|
| dim_date[date_key]        | fact_sales[date_key]    | 1 : *       | Single           |
| dim_product[product_key]  | fact_sales[product_key] | 1 : *       | Single           |
| dim_customer[customer_key]| fact_sales[customer_key]| 1 : *       | Single           |

## 3. Power Query clean-up
- `dim_date[full_date]` → change type to **Date**
- Mark `dim_date` as a **Date table** (Table tools → Mark as date table → `full_date`)
- Sort `month_name` by `month` (Column tools → Sort by column)
- Hide key columns and `revenue` / `cost` in the fact table (use measures instead)
