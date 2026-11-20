-- Builds the dashboard-ready summary table
CREATE OR REPLACE TABLE PRODUCT_DB.ANALYTICS.CATEGORY_SUMMARY AS
SELECT category,
       COUNT(*)                                   AS product_count,
       ROUND(SUM(price * stock), 2)               AS inventory_value,
       ROUND(AVG(rating), 2)                      AS avg_rating,
       SUM(CASE WHEN stock < 20 THEN 1 ELSE 0 END) AS low_stock_items,
       RANK() OVER (ORDER BY SUM(price * stock) DESC) AS value_rank
FROM PRODUCT_DB.RAW.PRODUCTS
GROUP BY category;
