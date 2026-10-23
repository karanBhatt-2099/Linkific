-- Q19: ROW_NUMBER vs RANK vs DENSE_RANK - how ties behave (compare the three columns)
SELECT p.name, p.unit_price,
       ROW_NUMBER() OVER (ORDER BY p.unit_price DESC) AS row_num,    -- always unique 1,2,3,4...
       RANK()       OVER (ORDER BY p.unit_price DESC) AS rnk,        -- ties share rank, then GAP
       DENSE_RANK() OVER (ORDER BY p.unit_price DESC) AS dense_rnk   -- ties share rank, NO gap
FROM products p
ORDER BY p.unit_price DESC
LIMIT 10;

-- Q20: PARTITION BY - top 2 products by revenue inside each category
WITH prod_rev AS (
    SELECT cat.name AS category, p.name AS product,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
    FROM order_items oi
    JOIN orders o       ON o.order_id = oi.order_id AND o.status = 'completed'
    JOIN products p     ON p.product_id = oi.product_id
    JOIN categories cat ON cat.category_id = p.category_id
    GROUP BY cat.name, p.name
),
ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC) AS rn
    FROM prod_rev
)
SELECT category, product, ROUND(revenue, 2) AS revenue, rn
FROM ranked
WHERE rn <= 2
ORDER BY category, rn;

-- Q21: Share of total using SUM() OVER () and a partitioned share
WITH cat_rev AS (
    SELECT cat.name AS category,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
    FROM order_items oi
    JOIN orders o       ON o.order_id = oi.order_id AND o.status = 'completed'
    JOIN products p     ON p.product_id = oi.product_id
    JOIN categories cat ON cat.category_id = p.category_id
    GROUP BY cat.name
)
SELECT category,
       ROUND(revenue, 2) AS revenue,
       ROUND(100.0 * revenue / SUM(revenue) OVER (), 1) AS pct_of_total,
       RANK() OVER (ORDER BY revenue DESC) AS rev_rank
FROM cat_rev
ORDER BY revenue DESC;

-- Q22: RUNNING TOTAL - cumulative monthly revenue (SUM OVER with ORDER BY)
WITH monthly AS (
    SELECT strftime('%Y-%m', o.order_date) AS month,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
    FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status = 'completed'
    GROUP BY month
)
SELECT month,
       ROUND(revenue, 2) AS revenue,
       ROUND(SUM(revenue) OVER (ORDER BY month), 2) AS running_total
FROM monthly
ORDER BY month
LIMIT 12;

-- Q23: RUNNING TOTAL per partition - cumulative revenue that RESETS each year
WITH monthly AS (
    SELECT strftime('%Y', o.order_date) AS year,
           strftime('%m', o.order_date) AS mon,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
    FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status = 'completed'
    GROUP BY year, mon
)
SELECT year, mon, ROUND(revenue, 2) AS revenue,
       ROUND(SUM(revenue) OVER (PARTITION BY year ORDER BY mon), 2) AS ytd_revenue
FROM monthly
ORDER BY year, mon
LIMIT 14;

-- Q24: LAG - month-over-month growth %
WITH monthly AS (
    SELECT strftime('%Y-%m', o.order_date) AS month,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
    FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status = 'completed'
    GROUP BY month
)
SELECT month,
       ROUND(revenue, 2) AS revenue,
       ROUND(LAG(revenue) OVER (ORDER BY month), 2) AS prev_month,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
             / LAG(revenue) OVER (ORDER BY month), 1) AS mom_growth_pct
FROM monthly
ORDER BY month
LIMIT 12;

-- Q25: LAG with offset 12 - year-over-year comparison for the same month
WITH monthly AS (
    SELECT strftime('%Y-%m', o.order_date) AS month,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
    FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status = 'completed'
    GROUP BY month
)
SELECT month,
       ROUND(revenue, 2) AS revenue,
       ROUND(LAG(revenue, 12) OVER (ORDER BY month), 2) AS same_month_last_year,
       ROUND(100.0 * (revenue - LAG(revenue, 12) OVER (ORDER BY month))
             / LAG(revenue, 12) OVER (ORDER BY month), 1) AS yoy_pct
FROM monthly
ORDER BY month DESC
LIMIT 6;

-- Q26: LEAD - days until each customer's NEXT order (and gap analysis)
WITH ordered AS (
    SELECT customer_id, order_id, order_date,
           LEAD(order_date) OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS next_order_date
    FROM orders
    WHERE status = 'completed'
)
SELECT customer_id, order_id, order_date, next_order_date,
       CAST(julianday(next_order_date) - julianday(order_date) AS INTEGER) AS days_to_next
FROM ordered
WHERE customer_id IN (1, 2)
ORDER BY customer_id, order_date
LIMIT 10;

-- Q27: MOVING AVERAGE - 3-month rolling average smooths volatility
WITH monthly AS (
    SELECT strftime('%Y-%m', o.order_date) AS month,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
    FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status = 'completed'
    GROUP BY month
)
SELECT month,
       ROUND(revenue, 2) AS revenue,
       ROUND(AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS ma_3m,
       ROUND(AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 5 PRECEDING AND CURRENT ROW), 2) AS ma_6m
FROM monthly
ORDER BY month
LIMIT 12;

-- Q28: NTILE + FIRST_VALUE - customer spend quartiles and gap to the top spender in their region
WITH spend AS (
    SELECT c.customer_id, c.name, c.region_id,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS total_spend
    FROM customers c
    JOIN orders o       ON o.customer_id = c.customer_id AND o.status = 'completed'
    JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY c.customer_id, c.name, c.region_id
)
SELECT name, region_id, ROUND(total_spend, 2) AS total_spend,
       NTILE(4) OVER (ORDER BY total_spend DESC) AS spend_quartile,
       ROUND(FIRST_VALUE(total_spend) OVER (PARTITION BY region_id ORDER BY total_spend DESC) - total_spend, 2) AS gap_to_region_top
FROM spend
ORDER BY total_spend DESC
LIMIT 8;
