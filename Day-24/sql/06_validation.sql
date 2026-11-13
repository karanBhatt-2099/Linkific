-- 06: Validation: counts, referential integrity, data quality. Results persisted in DW.validation_results
USE DATABASE {{DB}};
USE SCHEMA DW;

INSERT INTO validation_results (run_id, category, check_name, expected, actual, status)
SELECT '{{RUN_ID}}', category, check_name, expected, actual,
       IFF(actual = expected, 'PASS', IFF(severity = 'WARN','WARN','FAIL'))
FROM (
  -- Count checks
  SELECT 'COUNT' category, 'fact_sales rows = valid staging rows' check_name, 'FAIL' severity,
    (SELECT COUNT(DISTINCT sale_id) FROM {{DB}}.STG.stg_sales WHERE quantity>0) expected,
    (SELECT COUNT(*) FROM fact_sales) actual
  UNION ALL SELECT 'COUNT','dim_customer current rows = distinct staging customers','FAIL',
    (SELECT COUNT(DISTINCT customer_id) FROM {{DB}}.STG.stg_customers),
    (SELECT COUNT(*) FROM dim_customer WHERE is_current AND customer_key<>-1)
  UNION ALL SELECT 'COUNT','dim_product rows = distinct staging products','FAIL',
    (SELECT COUNT(DISTINCT product_id) FROM {{DB}}.STG.stg_products),
    (SELECT COUNT(*) FROM dim_product WHERE product_key<>-1)
  UNION ALL SELECT 'COUNT','dim_store rows = distinct staging stores','FAIL',
    (SELECT COUNT(DISTINCT store_id) FROM {{DB}}.STG.stg_stores),
    (SELECT COUNT(*) FROM dim_store WHERE store_key<>-1)
  UNION ALL SELECT 'COUNT','dim_date continuous (rows = day span)','FAIL',
    (SELECT DATEDIFF(day,MIN(full_date),MAX(full_date))+1 FROM dim_date),
    (SELECT COUNT(*) FROM dim_date)
  UNION ALL SELECT 'COUNT','sum(quantity) staging = fact','FAIL',
    (SELECT SUM(quantity) FROM {{DB}}.STG.stg_sales WHERE quantity>0),
    (SELECT SUM(quantity) FROM fact_sales)
  -- Referential integrity (expected 0 orphans)
  UNION ALL SELECT 'RI','fact.date_key not in dim_date','FAIL',0,
    (SELECT COUNT(*) FROM fact_sales f LEFT JOIN dim_date d ON d.date_key=f.date_key WHERE d.date_key IS NULL)
  UNION ALL SELECT 'RI','fact.customer_key not in dim_customer','FAIL',0,
    (SELECT COUNT(*) FROM fact_sales f LEFT JOIN dim_customer d ON d.customer_key=f.customer_key WHERE d.customer_key IS NULL)
  UNION ALL SELECT 'RI','fact.product_key not in dim_product','FAIL',0,
    (SELECT COUNT(*) FROM fact_sales f LEFT JOIN dim_product d ON d.product_key=f.product_key WHERE d.product_key IS NULL)
  UNION ALL SELECT 'RI','fact.store_key not in dim_store','FAIL',0,
    (SELECT COUNT(*) FROM fact_sales f LEFT JOIN dim_store d ON d.store_key=f.store_key WHERE d.store_key IS NULL)
  -- Data quality
  UNION ALL SELECT 'DQ','duplicate sale_id in fact','FAIL',0,
    (SELECT COUNT(*) FROM (SELECT sale_id FROM fact_sales GROUP BY 1 HAVING COUNT(*)>1))
  UNION ALL SELECT 'DQ','customers with !=1 current version','FAIL',0,
    (SELECT COUNT(*) FROM (SELECT customer_id FROM dim_customer GROUP BY 1 HAVING SUM(IFF(is_current,1,0))<>1))
  UNION ALL SELECT 'DQ','overlapping SCD2 versions','FAIL',0,
    (SELECT COUNT(*) FROM dim_customer a JOIN dim_customer b ON a.customer_id=b.customer_id
       AND a.customer_key<b.customer_key AND a.effective_date<b.end_date AND b.effective_date<a.end_date)
  UNION ALL SELECT 'DQ','NULL measures in fact','FAIL',0,
    (SELECT COUNT(*) FROM fact_sales WHERE quantity IS NULL OR net_amount IS NULL OR profit_amount IS NULL)
  UNION ALL SELECT 'DQ','net_amount <> gross - discount','FAIL',0,
    (SELECT COUNT(*) FROM fact_sales WHERE ABS(net_amount-(gross_amount-discount_amount))>0.01)
  UNION ALL SELECT 'DQ','negative/zero quantity in fact','FAIL',0,
    (SELECT COUNT(*) FROM fact_sales WHERE quantity<=0)
  UNION ALL SELECT 'DQ','fact rows mapped to Unknown customer (-1)','WARN',0,
    (SELECT COUNT(*) FROM fact_sales WHERE customer_key=-1)
  UNION ALL SELECT 'DQ','dim_customer with unclean email (case/space)','FAIL',0,
    (SELECT COUNT(*) FROM dim_customer WHERE email<>LOWER(TRIM(email)))
);

SELECT category, check_name, expected, actual, status FROM validation_results WHERE run_id = '{{RUN_ID}}' ORDER BY category, check_name;