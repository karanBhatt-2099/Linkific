-- 04: Dimension loads. Extract (staging) -> Transform/clean -> Load. Customer=SCD2, Product/Store=SCD1. Re-runnable.
USE DATABASE {{DB}};
USE SCHEMA DW;

-- Unknown members (-1) for late/orphan keys
INSERT INTO dim_customer (customer_key, customer_id, customer_name, email, city, segment, signup_date, effective_date, end_date, is_current, row_hash)
SELECT -1,'UNKNOWN','Unknown','unknown','Unknown','Unknown',NULL,'1900-01-01','9999-12-31',TRUE,'-'
WHERE NOT EXISTS (SELECT 1 FROM dim_customer WHERE customer_key=-1);
INSERT INTO dim_product (product_key, product_id, product_name, category, brand, unit_cost, list_price)
SELECT -1,'UNKNOWN','Unknown','Unknown','Unknown',0,0 WHERE NOT EXISTS (SELECT 1 FROM dim_product WHERE product_key=-1);
INSERT INTO dim_store (store_key, store_id, store_name, city, region, open_date)
SELECT -1,'UNKNOWN','Unknown','Unknown','Unknown',NULL WHERE NOT EXISTS (SELECT 1 FROM dim_store WHERE store_key=-1);

-- ---------- Customer (SCD2: track city + segment) ----------
CREATE OR REPLACE TEMP TABLE tmp_customer AS
WITH c AS (
  SELECT customer_id,
    INITCAP(TRIM(customer_name)) AS customer_name,
    LOWER(TRIM(email)) AS email,
    COALESCE(NULLIF(TRIM(city),''),'Unknown') AS city,
    COALESCE(NULLIF(TRIM(segment),''),'Unknown') AS segment,
    signup_date
  FROM {{DB}}.STG.stg_customers
  QUALIFY ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY signup_date DESC) = 1
)
SELECT *, MD5(city||'|'||segment) AS row_hash FROM c;

-- 1) close changed current rows
UPDATE dim_customer d
SET end_date = CURRENT_DATE(), is_current = FALSE
FROM tmp_customer s
WHERE d.customer_id = s.customer_id AND d.is_current AND d.row_hash <> s.row_hash;

-- 2) insert new customers + new versions of changed ones
INSERT INTO dim_customer (customer_id, customer_name, email, city, segment, signup_date, effective_date, end_date, is_current, row_hash)
SELECT s.customer_id, s.customer_name, s.email, s.city, s.segment, s.signup_date,
  IFF(h.n IS NULL, '1900-01-01'::DATE, CURRENT_DATE()),    -- first version covers all history
  '9999-12-31'::DATE, TRUE, s.row_hash
FROM tmp_customer s
LEFT JOIN dim_customer cur ON cur.customer_id = s.customer_id AND cur.is_current
LEFT JOIN (SELECT customer_id, COUNT(*) n FROM dim_customer GROUP BY 1) h ON h.customer_id = s.customer_id
WHERE cur.customer_key IS NULL;

-- ---------- Product (SCD1 overwrite) ----------
MERGE INTO dim_product t
USING (SELECT product_id, INITCAP(TRIM(product_name)) product_name, COALESCE(INITCAP(TRIM(category)),'Unknown') category,
              COALESCE(INITCAP(TRIM(brand)),'Unknown') brand, unit_cost, list_price
       FROM {{DB}}.STG.stg_products
       QUALIFY ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY product_id)=1) s
ON t.product_id = s.product_id
WHEN MATCHED THEN UPDATE SET product_name=s.product_name, category=s.category, brand=s.brand, unit_cost=s.unit_cost, list_price=s.list_price
WHEN NOT MATCHED THEN INSERT (product_id, product_name, category, brand, unit_cost, list_price)
  VALUES (s.product_id, s.product_name, s.category, s.brand, s.unit_cost, s.list_price);

-- ---------- Store (SCD1 overwrite) ----------
MERGE INTO dim_store t
USING (SELECT store_id, INITCAP(TRIM(store_name)) store_name, COALESCE(INITCAP(TRIM(city)),'Unknown') city,
              COALESCE(INITCAP(TRIM(region)),'Unknown') region, open_date
       FROM {{DB}}.STG.stg_stores
       QUALIFY ROW_NUMBER() OVER (PARTITION BY store_id ORDER BY store_id)=1) s
ON t.store_id = s.store_id
WHEN MATCHED THEN UPDATE SET store_name=s.store_name, city=s.city, region=s.region, open_date=s.open_date
WHEN NOT MATCHED THEN INSERT (store_id, store_name, city, region, open_date)
  VALUES (s.store_id, s.store_name, s.city, s.region, s.open_date);
