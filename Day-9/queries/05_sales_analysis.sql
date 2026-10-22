
-- Q42: Monthly sales dashboard - revenue, orders, AOV, units in one table
SELECT strftime('%Y-%m', o.order_date) AS month,
       COUNT(DISTINCT o.order_id) AS orders,
       SUM(oi.quantity) AS units,
       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS revenue,
       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.status = 'completed'
GROUP BY month
ORDER BY month DESC
LIMIT 6;

-- Q43: Quarterly revenue by region with rank inside each quarter
WITH q AS (
    SELECT strftime('%Y', o.order_date) || '-Q' || ((CAST(strftime('%m', o.order_date) AS INTEGER) + 2) / 3) AS quarter,
           r.region_name,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN customers c    ON c.customer_id = o.customer_id
    JOIN regions r      ON r.region_id = c.region_id
    WHERE o.status = 'completed'
    GROUP BY quarter, r.region_name
)
SELECT quarter, region_name, ROUND(revenue, 2) AS revenue,
       RANK() OVER (PARTITION BY quarter ORDER BY revenue DESC) AS rank_in_quarter
FROM q
ORDER BY quarter DESC, rank_in_quarter
LIMIT 8;

-- Q44: Day-of-week seasonality - which weekday sells most
SELECT CASE strftime('%w', o.order_date)
            WHEN '0' THEN 'Sun' WHEN '1' THEN 'Mon' WHEN '2' THEN 'Tue' WHEN '3' THEN 'Wed'
            WHEN '4' THEN 'Thu' WHEN '5' THEN 'Fri' ELSE 'Sat' END AS weekday,
       COUNT(DISTINCT o.order_id) AS orders,
       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS revenue
FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.status = 'completed'
GROUP BY strftime('%w', o.order_date)
ORDER BY strftime('%w', o.order_date);

-- Q45: Rep leaderboard with quota attainment (quota = 1.25 x average rep) and rank
WITH rep_rev AS (
    SELECT e.employee_id, e.name,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
    FROM orders o
    JOIN employees e    ON e.employee_id = o.employee_id
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status = 'completed'
    GROUP BY e.employee_id, e.name
)
SELECT name,
       ROUND(revenue, 2) AS revenue,
       DENSE_RANK() OVER (ORDER BY revenue DESC) AS rank,
       ROUND(100.0 * revenue / (1.25 * AVG(revenue) OVER ()), 1) AS quota_attainment_pct
FROM rep_rev
ORDER BY revenue DESC;

-- Q46: New vs returning customers per month (cohort-style, using MIN order date per customer)
WITH first_order AS (
    SELECT customer_id, MIN(order_date) AS first_date
    FROM orders WHERE status = 'completed'
    GROUP BY customer_id
)
SELECT strftime('%Y-%m', o.order_date) AS month,
       COUNT(DISTINCT CASE WHEN o.order_date = f.first_date THEN o.customer_id END) AS new_customers,
       COUNT(DISTINCT CASE WHEN o.order_date > f.first_date THEN o.customer_id END) AS returning_customers
FROM orders o
JOIN first_order f ON f.customer_id = o.customer_id
WHERE o.status = 'completed'
GROUP BY month
ORDER BY month DESC
LIMIT 6;

-- Q47: Market basket - product pairs most often bought together (self join on order_items)
SELECT p1.name AS product_a, p2.name AS product_b, COUNT(*) AS times_together
FROM order_items a
JOIN order_items b ON a.order_id = b.order_id AND a.product_id < b.product_id
JOIN products p1   ON p1.product_id = a.product_id
JOIN products p2   ON p2.product_id = b.product_id
GROUP BY p1.name, p2.name
ORDER BY times_together DESC, product_a
LIMIT 6;

-- Q48: Pareto / ABC analysis - what % of products drive 80% of revenue
WITH prod AS (
    SELECT p.name, SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
    FROM order_items oi
    JOIN orders o   ON o.order_id = oi.order_id AND o.status = 'completed'
    JOIN products p ON p.product_id = oi.product_id
    GROUP BY p.name
),
cum AS (
    SELECT name, revenue,
           SUM(revenue) OVER (ORDER BY revenue DESC) * 1.0 / SUM(revenue) OVER () AS cum_share
    FROM prod
)
SELECT name, ROUND(revenue, 2) AS revenue, ROUND(100 * cum_share, 1) AS cumulative_pct,
       CASE WHEN cum_share <= 0.80 THEN 'A' WHEN cum_share <= 0.95 THEN 'B' ELSE 'C' END AS abc_class
FROM cum
ORDER BY revenue DESC;

-- Q49: Customer retention - months between first and each later order (cohort age)
WITH first_o AS (
    SELECT customer_id, strftime('%Y-%m', MIN(order_date)) AS cohort
    FROM orders WHERE status = 'completed' GROUP BY customer_id
)
SELECT f.cohort,
       COUNT(DISTINCT f.customer_id) AS cohort_size,
       COUNT(DISTINCT CASE WHEN strftime('%Y-%m', o.order_date) > f.cohort THEN f.customer_id END) AS came_back_later
FROM first_o f
JOIN orders o ON o.customer_id = f.customer_id AND o.status = 'completed'
GROUP BY f.cohort
ORDER BY f.cohort
LIMIT 6;

-- Q50: Best-selling product per region using ROW_NUMBER over a multi-join CTE
WITH rp AS (
    SELECT r.region_name, p.name AS product,
           SUM(oi.quantity) AS units,
           ROW_NUMBER() OVER (PARTITION BY r.region_name ORDER BY SUM(oi.quantity) DESC) AS rn
    FROM order_items oi
    JOIN orders o    ON o.order_id = oi.order_id AND o.status = 'completed'
    JOIN customers c ON c.customer_id = o.customer_id
    JOIN regions r   ON r.region_id = c.region_id
    JOIN products p  ON p.product_id = oi.product_id
    GROUP BY r.region_name, p.name
)
SELECT region_name, product, units FROM rp WHERE rn = 1 ORDER BY region_name;
