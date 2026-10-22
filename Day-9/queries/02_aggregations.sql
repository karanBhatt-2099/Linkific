-- =====================================================================
-- 02_AGGREGATIONS.SQL : GROUP BY, HAVING, multi-aggregates, DISTINCT, ROLLUP/CUBE
-- =====================================================================

-- Q11: GROUP BY - revenue per category
SELECT cat.name AS category,
       SUM(oi.quantity) AS units,
       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS revenue
FROM order_items oi
JOIN orders o       ON o.order_id = oi.order_id AND o.status = 'completed'
JOIN products p     ON p.product_id = oi.product_id
JOIN categories cat ON cat.category_id = p.category_id
GROUP BY cat.name
ORDER BY revenue DESC;

-- Q12: HAVING - customers with more than 10 completed orders (filter AFTER aggregation)
SELECT c.name, COUNT(*) AS orders
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.status = 'completed'          -- WHERE filters rows before grouping
GROUP BY c.customer_id, c.name
HAVING COUNT(*) > 10                  -- HAVING filters groups after grouping
ORDER BY orders DESC;

-- Q13: MULTIPLE AGGREGATIONS - one pass, many metrics per product
SELECT p.name,
       COUNT(*)                       AS line_items,
       SUM(oi.quantity)               AS units,
       ROUND(AVG(oi.discount) * 100, 1) AS avg_discount_pct,
       MIN(oi.discount)               AS min_disc,
       MAX(oi.discount)               AS max_disc,
       ROUND(SUM(oi.quantity * (oi.unit_price * (1 - oi.discount) - p.unit_cost)), 2) AS gross_profit
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o   ON o.order_id = oi.order_id AND o.status = 'completed'
GROUP BY p.product_id, p.name
ORDER BY gross_profit DESC
LIMIT 8;

-- Q14: COUNT DISTINCT - unique customers and products per month vs raw order counts
SELECT strftime('%Y-%m', o.order_date) AS month,
       COUNT(*)                        AS order_rows,
       COUNT(DISTINCT o.customer_id)   AS unique_customers,
       COUNT(DISTINCT oi.product_id)   AS unique_products
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.status = 'completed'
GROUP BY month
ORDER BY month
LIMIT 6;

-- Q15: CONDITIONAL AGGREGATION (FILTER / CASE) - status mix per region in a single row
SELECT r.region_name,
       COUNT(*)                                           AS total_orders,
       COUNT(*) FILTER (WHERE o.status = 'completed')     AS completed,
       COUNT(*) FILTER (WHERE o.status = 'cancelled')     AS cancelled,
       COUNT(*) FILTER (WHERE o.status = 'returned')      AS returned,
       ROUND(100.0 * SUM(CASE WHEN o.status = 'returned' THEN 1 ELSE 0 END) / COUNT(*), 1) AS return_rate_pct
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN regions r   ON r.region_id = c.region_id
GROUP BY r.region_name
ORDER BY total_orders DESC;

-- Q16: HAVING with an aggregate vs. aggregate comparison - products whose average discount beats the store average
SELECT p.name, ROUND(AVG(oi.discount), 4) AS avg_discount
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.product_id, p.name
HAVING AVG(oi.discount) > (SELECT AVG(discount) FROM order_items)
ORDER BY avg_discount DESC;

-- Q17: ROLLUP (emulated) - region subtotals and grand total.
-- SQLite lacks ROLLUP, so we UNION ALL the grouping levels.
-- PostgreSQL/MySQL/SQL Server equivalent:  GROUP BY ROLLUP (region_name, year)
WITH base AS (
    SELECT r.region_name,
           strftime('%Y', o.order_date) AS year,
           oi.quantity * oi.unit_price * (1 - oi.discount) AS rev
    FROM order_items oi
    JOIN orders o    ON o.order_id = oi.order_id AND o.status = 'completed'
    JOIN customers c ON c.customer_id = o.customer_id
    JOIN regions r   ON r.region_id = c.region_id
)
SELECT region_name, year, ROUND(SUM(rev), 2) AS revenue FROM base GROUP BY region_name, year
UNION ALL
SELECT region_name, 'ALL YEARS', ROUND(SUM(rev), 2) FROM base GROUP BY region_name          -- subtotal
UNION ALL
SELECT 'ALL REGIONS', 'ALL YEARS', ROUND(SUM(rev), 2) FROM base                             -- grand total
ORDER BY 1, 2;

-- Q18: CUBE (emulated) - every combination of (region, category-root) subtotals
-- Native:  GROUP BY CUBE (region_name, category)   -> 2^2 = 4 grouping sets
WITH base AS (
    SELECT r.region_name,
           COALESCE(parent.name, cat.name) AS category,
           oi.quantity * oi.unit_price * (1 - oi.discount) AS rev
    FROM order_items oi
    JOIN orders o       ON o.order_id = oi.order_id AND o.status = 'completed'
    JOIN customers c    ON c.customer_id = o.customer_id
    JOIN regions r      ON r.region_id = c.region_id
    JOIN products p     ON p.product_id = oi.product_id
    JOIN categories cat ON cat.category_id = p.category_id
    LEFT JOIN categories parent ON parent.category_id = cat.parent_id
)
SELECT region_name, category, ROUND(SUM(rev),2) AS revenue FROM base GROUP BY region_name, category   -- (region, category)
UNION ALL SELECT region_name, '*', ROUND(SUM(rev),2) FROM base GROUP BY region_name                    -- (region)
UNION ALL SELECT '*', category, ROUND(SUM(rev),2) FROM base GROUP BY category                          -- (category)
UNION ALL SELECT '*', '*', ROUND(SUM(rev),2) FROM base                                                 -- ()
ORDER BY 1, 2
LIMIT 14;
