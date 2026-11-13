-- 05: Fact load: extract -> surrogate key lookups (point-in-time for SCD2 customer) -> measures -> load. Idempotent on sale_id.
USE DATABASE {{DB}};
USE SCHEMA DW;

INSERT INTO fact_sales (sale_id, order_id, date_key, customer_key, product_key, store_key,
  quantity, unit_price, discount_pct, gross_amount, discount_amount, net_amount, cost_amount, profit_amount)
WITH src AS (
  SELECT s.*, COALESCE(c.customer_key,-1) AS customer_key, COALESCE(p.product_key,-1) AS product_key,
         COALESCE(st.store_key,-1) AS store_key,
         COALESCE(p.list_price,0) AS unit_price, COALESCE(p.unit_cost,0) AS unit_cost
  FROM {{DB}}.STG.stg_sales s
  LEFT JOIN dim_customer c ON c.customer_id = s.customer_id
        AND s.order_date >= c.effective_date AND s.order_date < c.end_date
  LEFT JOIN dim_product p  ON p.product_id = s.product_id
  LEFT JOIN dim_store st   ON st.store_id  = s.store_id
  WHERE s.quantity > 0                                   -- reject non-positive quantities
    AND NOT EXISTS (SELECT 1 FROM fact_sales f WHERE f.sale_id = s.sale_id)
  QUALIFY ROW_NUMBER() OVER (PARTITION BY s.sale_id ORDER BY s.order_date) = 1
), m AS (
  SELECT *, ROUND(quantity*unit_price,2) AS gross_amount,
            ROUND(quantity*unit_price*discount_pct/100,2) AS discount_amount
  FROM src
)
SELECT sale_id, order_id, TO_NUMBER(TO_CHAR(order_date,'YYYYMMDD')), customer_key, product_key, store_key,
  quantity, unit_price, discount_pct, gross_amount, discount_amount,
  gross_amount - discount_amount,
  ROUND(quantity*unit_cost,2),
  gross_amount - discount_amount - ROUND(quantity*unit_cost,2)
FROM m;
