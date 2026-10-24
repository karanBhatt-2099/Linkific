SELECT '1. Row counts (dates=730, customers=10, products=12, stores=4, facts=27)' AS check_name,
       CASE WHEN (SELECT COUNT(*) FROM dw.dim_date)=730
             AND (SELECT COUNT(*) FROM dw.dim_customer)=10
             AND (SELECT COUNT(*) FROM dw.dim_product)=12
             AND (SELECT COUNT(*) FROM dw.dim_store)=4
             AND (SELECT COUNT(*) FROM dw.fact_sales)=27
            THEN 'PASS' ELSE 'FAIL' END AS status
UNION ALL
SELECT '2. No orphan foreign keys in fact_sales',
       CASE WHEN (SELECT COUNT(*) FROM dw.fact_sales f
                  LEFT JOIN dw.dim_date     d ON d.date_key     = f.date_key
                  LEFT JOIN dw.dim_customer c ON c.customer_key = f.customer_key
                  LEFT JOIN dw.dim_product  p ON p.product_key  = f.product_key
                  LEFT JOIN dw.dim_store    s ON s.store_key    = f.store_key
                  WHERE d.date_key IS NULL OR c.customer_key IS NULL
                     OR p.product_key IS NULL OR s.store_key IS NULL) = 0
            THEN 'PASS' ELSE 'FAIL' END
UNION ALL
SELECT '3. Grain: no duplicate (order_id, order_line_number)',
       CASE WHEN (SELECT COUNT(*) FROM (SELECT order_id, order_line_number
                                        FROM dw.fact_sales
                                        GROUP BY 1,2 HAVING COUNT(*)>1) x) = 0
            THEN 'PASS' ELSE 'FAIL' END
UNION ALL
SELECT '4. Measures reconcile: profit = sales - cost',
       CASE WHEN (SELECT COUNT(*) FROM dw.fact_sales
                  WHERE profit_amount <> sales_amount - cost_amount) = 0
            THEN 'PASS' ELSE 'FAIL' END
UNION ALL
SELECT '5. Measures reconcile: sales = qty*price - discount',
       CASE WHEN (SELECT COUNT(*) FROM dw.fact_sales
                  WHERE sales_amount <> quantity*unit_price - discount_amount) = 0
            THEN 'PASS' ELSE 'FAIL' END
UNION ALL
SELECT '6. Exactly one current row per customer_id',
       CASE WHEN (SELECT COUNT(*) FROM (SELECT customer_id FROM dw.dim_customer
                                        WHERE is_current GROUP BY 1 HAVING COUNT(*)<>1) x) = 0
            THEN 'PASS' ELSE 'FAIL' END
UNION ALL
SELECT '7. Total sales = 776250.00',
       CASE WHEN (SELECT SUM(sales_amount) FROM dw.fact_sales) = 776250.00
            THEN 'PASS' ELSE 'FAIL' END
UNION ALL
SELECT '8. Snowflake and star give the same total sales',
       CASE WHEN (SELECT SUM(sales_amount) FROM dw.fact_sales)
               = (SELECT SUM(sales_amount) FROM dw_snowflake.fact_sales)
            THEN 'PASS' ELSE 'FAIL' END
UNION ALL
SELECT '9. Galaxy: fact_inventory has 288 rows and no orphans',
       CASE WHEN (SELECT COUNT(*) FROM dw.fact_inventory)=288
             AND (SELECT COUNT(*) FROM dw.fact_inventory i
                  LEFT JOIN dw.dim_product p ON p.product_key=i.product_key
                  LEFT JOIN dw.dim_store   s ON s.store_key=i.store_key
                  WHERE p.product_key IS NULL OR s.store_key IS NULL)=0
            THEN 'PASS' ELSE 'FAIL' END;
