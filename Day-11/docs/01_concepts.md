# 01 - Data Warehouse Concepts (in plain language)

## The big picture with a shop example
Imagine a shop owner. During the day the cashier records every sale in a system.
At the end of the quarter the owner asks: *"Which category earned the most profit, and in which region?"*
The cashier's system is built for **fast small writes**, not for answering big questions across millions of rows.
So we copy the data into a second system designed for **questions**. That second system is the **data warehouse**.

## OLTP vs OLAP

| | OLTP (operations) | OLAP (analytics) |
|---|---|---|
| Purpose | Run the business day-to-day | Analyse the business |
| Example | Billing app, ATM, order entry | Sales dashboard, quarterly report |
| Typical query | `INSERT` one order, `UPDATE` one address | `SUM` sales for 3 years grouped by region |
| Data | Current, detailed | Historical, integrated, often summarised |
| Design | Normalized (3NF), many small tables | Dimensional (star), fewer, wider tables |
| Users | Thousands of clerks/customers | Analysts, managers |
| Speed goal | Milliseconds per transaction | Seconds for huge scans |

## Database vs Data Warehouse vs Data Mart
* **Database** - any organised store of data (our PostgreSQL server holds many).
* **Data warehouse (DW)** - one database *designed for analysis*: subject-oriented, integrated from many sources, historical, and (mostly) read-only for users.
* **Data mart** - a small slice of the warehouse for one team (e.g. a *Sales mart* for the sales team, a *Finance mart*). In this project `dw` is effectively a Sales mart.

## Typical architecture
```
Source systems          Staging            Warehouse                 Consumers
(ERP, CRM, web app) --> (raw copy)  --ETL--> (dim + fact tables) --> (SQL, BI dashboards)
   OLTP databases        landing area        star schema / marts
```
* **ETL** = Extract (read from source), Transform (clean, map keys, calculate), Load (write to warehouse).
* In this project the "source" is typed-in `VALUES` lists and the staging idea appears in the SCD scripts (`stg_customer`).

## Vocabulary you will use every day
| Term | Meaning | Example in this project |
|---|---|---|
| **Fact table** | Events/transactions with numbers | `dw.fact_sales` |
| **Dimension table** | Descriptive context used to slice facts | `dw.dim_product` |
| **Grain** | What exactly one fact row represents | one product line on one order |
| **Measure** | A number you aggregate | `sales_amount`, `quantity` |
| **Surrogate key** | Meaningless warehouse-made integer key | `customer_key` |
| **Natural (business) key** | ID from the source system | `customer_id = 'C001'` |
| **Degenerate dimension** | An ID kept in the fact table with no dimension table | `order_id` |
| **Conformed dimension** | One dimension shared by several facts with identical meaning | `dim_date`, `dim_product`, `dim_store` |
| **Slowly Changing Dimension** | Technique for handling changed dimension attributes | SCD 1/2/3 |

## Types of measures
* **Additive** - can be summed across all dimensions (`sales_amount`).
* **Semi-additive** - can be summed across some dimensions but not time (`quantity_on_hand`: do not add January + February stock!).
* **Non-additive** - never summed (ratios such as `profit_margin_pct`; store the numerator and denominator instead).

## Why surrogate keys?
1. Source IDs can change or be reused.
2. They allow **history** (SCD Type 2 creates several rows for the same `customer_id`).
3. Small integers make joins fast.
4. Data from multiple sources can be unified.
