# Expected Outputs

Real outputs captured by running every script in order on PostgreSQL 16. Your numbers should match exactly (surrogate keys can differ only if you re-ran scripts without TRUNCATE ... RESTART IDENTITY).


## Create schemas
`00_setup/02_create_schemas.sql`

```text
 schema_name  
--------------
 dw
 dw_snowflake
 scd_demo
(3 rows)
```


## Load dimensions (row counts)
`02_data/01_load_dimensions.sql`

```text
 dates | customers | products | stores 
-------+-----------+----------+--------
   730 |        10 |       12 |      4
(1 row)
```


## Load fact_sales
`02_data/02_load_fact_sales.sql`

```text
 fact_rows | total_sales | total_profit 
-----------+-------------+--------------
        27 |   776250.00 |    206150.00
(1 row)
```


## Load snowflake + galaxy
`02_data/03_load_snowflake_and_galaxy.sql`

```text
 snowflake_fact_rows | inventory_rows 
---------------------+----------------
                  27 |            288
(1 row)
```


## SCD Type 1 - before and after
`03_scd/01_scd_type1_overwrite.sql`

```text
 customer_key | customer_id |  full_name   |          email          |   city    
--------------+-------------+--------------+-------------------------+-----------
            1 | C001        | Aarav Sharma | aarav.old@example.com   | Mumbai
            2 | C002        | Priya Patel  | priya.patel@example.com | Ahmedabad
            3 | C003        | Rahul Verma  | rahul.verma@example.com | Delhi
(3 rows)

 customer_key | customer_id |  full_name   |          email           |  city   
--------------+-------------+--------------+--------------------------+---------
            1 | C001        | Aarav Sharma | aarav.sharma@example.com | Mumbai
            2 | C002        | Priya Patel  | priya.patel@example.com  | Surat
            3 | C003        | Rahul Verma  | rahul.verma@example.com  | Delhi
            4 | C004        | Sneha Iyer   | sneha.iyer@example.com   | Chennai
(4 rows)

 four_rows | no_duplicates | priya_in_surat 
-----------+---------------+----------------
 t         | t             | t
(1 row)
```


## SCD Type 2 - history + point-in-time facts
`03_scd/02_scd_type2_history.sql`

```text
 customer_key | customer_id |   city    | effective_date |  end_date  | is_current 
--------------+-------------+-----------+----------------+------------+------------
            1 | C001        | Mumbai    | 2025-01-01     | 2026-05-31 | f
            3 | C001        | Pune      | 2026-06-01     | 9999-12-31 | t
            2 | C002        | Ahmedabad | 2025-01-01     | 9999-12-31 | t
            4 | C003        | Delhi     | 2026-06-01     | 9999-12-31 | t
(4 rows)

   city    | total_sales 
-----------+-------------
 Ahmedabad |     3000.00
 Mumbai    |     5000.00
 Pune      |     7000.00
(3 rows)
```


## SCD Type 3 - current and previous value
`03_scd/03_scd_type3_previous_value.sql`

```text
 customer_id | current_city | previous_city | city_changed_date 
-------------+--------------+---------------+-------------------
 C001        | Mumbai       |               | 
 C002        | Surat        | Ahmedabad     | 2026-06-01
(2 rows)

 customer_id | current_city | previous_city | city_changed_date 
-------------+--------------+---------------+-------------------
 C001        | Mumbai       |               | 
 C002        | Vadodara     | Surat         | 2026-09-01
(2 rows)

 type3_works 
-------------
 t
(1 row)
```


## Validation - star schema
`04_validation/01_validate_star_schema.sql`

```text
                                check_name                                | status 
--------------------------------------------------------------------------+--------
 1. Row counts (dates=730, customers=10, products=12, stores=4, facts=27) | PASS
 2. No orphan foreign keys in fact_sales                                  | PASS
 3. Grain: no duplicate (order_id, order_line_number)                     | PASS
 4. Measures reconcile: profit = sales - cost                             | PASS
 5. Measures reconcile: sales = qty*price - discount                      | PASS
 6. Exactly one current row per customer_id                               | PASS
 7. Total sales = 776250.00                                               | PASS
 8. Snowflake and star give the same total sales                          | PASS
 9. Galaxy: fact_inventory has 288 rows and no orphans                    | PASS
(9 rows)
```


## Validation - SCD demos
`04_validation/02_validate_scd.sql`

```text
                        check_name                         | status 
-----------------------------------------------------------+--------
 SCD1: Priya overwritten to Surat, 4 rows                  | PASS
 SCD2: Aarav has 2 versions, only 1 current (Pune)         | PASS
 SCD2: no overlapping date ranges                          | PASS
 SCD2: history preserved in facts (Mumbai=5000, Pune=7000) | PASS
 SCD3: Priya current=Vadodara, previous=Surat              | PASS
(5 rows)
```


## Business queries Q1-Q9
`05_analytics/01_business_queries.sql`

```text
 total_sales | total_profit | profit_margin_pct 
-------------+--------------+-------------------
   776250.00 |    206150.00 |              26.6
(1 row)

 year | month_number | month_name | total_sales 
------+--------------+------------+-------------
 2026 |            1 | January    |   166000.00
 2026 |            2 | February   |   253750.00
 2026 |            3 | March      |   195200.00
 2026 |            4 | April      |    81800.00
 2026 |            5 | May        |    64000.00
 2026 |            6 | June       |    15500.00
(6 rows)

  category   | units_sold | total_sales | total_profit 
-------------+------------+-------------+--------------
 Electronics |         25 |   632900.00 |    148700.00
 Furniture   |         18 |   138400.00 |     54900.00
 Stationery  |         19 |     4950.00 |      2550.00
(3 rows)

 region |     store_name      | total_sales 
--------+---------------------+-------------
 South  | Bengaluru Tech Park |   402500.00
 North  | Delhi Central       |   173700.00
 West   | Mumbai Flagship     |   145800.00
 Online | Online Store        |    54250.00
(4 rows)

 customer_id |  full_name   |  segment  | total_sales 
-------------+--------------+-----------+-------------
 C005        | Vikram Singh | Corporate |   268500.00
 C009        | Arjun Reddy  | Corporate |   150000.00
 C002        | Priya Patel  | Corporate |   106200.00
 C001        | Aarav Sharma | Consumer  |    72300.00
 C007        | Rohan Mehta  | Consumer  |    65000.00
(5 rows)

 year | quarter |  category   | total_sales 
------+---------+-------------+-------------
 2026 |       1 | Electronics |   527300.00
 2026 |       1 | Furniture   |    83900.00
 2026 |       1 | Stationery  |     3750.00
 2026 |       1 |             |   614950.00
 2026 |       2 | Electronics |   105600.00
 2026 |       2 | Furniture   |    54500.00
 2026 |       2 | Stationery  |     1200.00
 2026 |       2 |             |   161300.00
 2026 |         |             |   776250.00
      |         |             |   776250.00
(10 rows)

 month_name | monthly_sales | running_total 
------------+---------------+---------------
 January    |     166000.00 |     166000.00
 February   |     253750.00 |     419750.00
 March      |     195200.00 |     614950.00
 April      |      81800.00 |     696750.00
 May        |      64000.00 |     760750.00
 June       |      15500.00 |     776250.00
(6 rows)

 category_name | total_sales 
---------------+-------------
 Electronics   |   632900.00
 Furniture     |   138400.00
 Stationery    |     4950.00
(3 rows)

 month_number |  category   |   sales   | units_in_stock 
--------------+-------------+-----------+----------------
            1 | Electronics |  95800.00 |            656
            1 | Furniture   |  70200.00 |            376
            1 | Stationery  |         0 |            152
            2 | Electronics | 250000.00 |            576
            2 | Furniture   |         0 |            456
            2 | Stationery  |   3750.00 |            192
(6 rows)
```
