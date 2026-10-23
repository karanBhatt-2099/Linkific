-- Q29: Subquery in WHERE (IN) - customers who bought a product priced above 500
SELECT DISTINCT c.name
FROM customers c
WHERE c.customer_id IN (
    SELECT o.customer_id
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE oi.unit_price > 500
)
ORDER BY c.name
LIMIT 8;

-- Q30: Subquery in WHERE (scalar compare) - orders larger than the average order value
SELECT o.order_id, ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS order_value
FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY o.order_id
HAVING SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) >
       (SELECT AVG(v) FROM (SELECT SUM(quantity * unit_price * (1 - discount)) AS v
                            FROM order_items GROUP BY order_id))
ORDER BY order_value DESC
LIMIT 5;

-- Q31: Subquery in SELECT - each region's revenue next to the company total
SELECT r.region_name,
       ROUND((SELECT SUM(oi.quantity * oi.unit_price * (1 - oi.discount))
              FROM order_items oi
              JOIN orders o    ON o.order_id = oi.order_id AND o.status = 'completed'
              JOIN customers c ON c.customer_id = o.customer_id
              WHERE c.region_id = r.region_id), 2) AS region_revenue,
       ROUND((SELECT SUM(quantity * unit_price * (1 - discount))
              FROM order_items oi JOIN orders o ON o.order_id = oi.order_id
              WHERE o.status = 'completed'), 2) AS company_revenue
FROM regions r;

-- Q32: Subquery in FROM (derived table) - average of per-customer order counts
SELECT ROUND(AVG(order_cnt), 2) AS avg_orders_per_customer,
       MAX(order_cnt) AS max_orders
FROM (SELECT customer_id, COUNT(*) AS order_cnt
      FROM orders WHERE status = 'completed'
      GROUP BY customer_id) AS per_customer;

-- Q33: CORRELATED subquery - each product vs the average price of ITS OWN category
SELECT p.name, p.unit_price,
       (SELECT ROUND(AVG(p2.unit_price), 2) FROM products p2 WHERE p2.category_id = p.category_id) AS category_avg
FROM products p
WHERE p.unit_price > (SELECT AVG(p2.unit_price) FROM products p2 WHERE p2.category_id = p.category_id)
ORDER BY p.unit_price DESC;

-- Q34: CORRELATED EXISTS / NOT EXISTS - products never sold in a completed order
SELECT p.product_id, p.name
FROM products p
WHERE NOT EXISTS (
    SELECT 1
    FROM order_items oi
    JOIN orders o ON o.order_id = oi.order_id
    WHERE oi.product_id = p.product_id AND o.status = 'completed'
);

-- Q35: CORRELATED subquery - most recent order for every customer (latest-row-per-group)
SELECT o.customer_id, o.order_id, o.order_date
FROM orders o
WHERE o.order_date = (SELECT MAX(o2.order_date) FROM orders o2 WHERE o2.customer_id = o.customer_id)
  AND o.customer_id <= 6
ORDER BY o.customer_id, o.order_id;

-- Q36: Single CTE - readable version of "customers above average spend"
WITH spend AS (
    SELECT o.customer_id, SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS total
    FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status = 'completed'
    GROUP BY o.customer_id
)
SELECT c.name, ROUND(s.total, 2) AS total
FROM spend s
JOIN customers c ON c.customer_id = s.customer_id
WHERE s.total > (SELECT AVG(total) FROM spend)
ORDER BY s.total DESC
LIMIT 6;

-- Q37: MULTIPLE (chained) CTEs - customer segmentation: Champion / Regular / At-risk
WITH customer_stats AS (
    SELECT c.customer_id, c.name,
           COUNT(DISTINCT o.order_id) AS orders,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS spend,
           MAX(o.order_date) AS last_order
    FROM customers c
    JOIN orders o       ON o.customer_id = c.customer_id AND o.status = 'completed'
    JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY c.customer_id, c.name
),
reference AS (
    SELECT MAX(order_date) AS as_of FROM orders
),
scored AS (
    SELECT cs.*, CAST(julianday(r.as_of) - julianday(cs.last_order) AS INTEGER) AS days_inactive
    FROM customer_stats cs CROSS JOIN reference r
)
SELECT CASE WHEN spend >= 6000 AND days_inactive <= 90 THEN 'Champion'
            WHEN days_inactive > 180                    THEN 'At-risk'
            ELSE 'Regular' END AS segment,
       COUNT(*) AS customers,
       ROUND(AVG(spend), 2) AS avg_spend,
       ROUND(AVG(days_inactive), 0) AS avg_days_inactive
FROM scored
GROUP BY segment
ORDER BY avg_spend DESC;

-- Q38: RECURSIVE CTE - org chart with depth and full reporting path
WITH RECURSIVE org AS (
    SELECT employee_id, name, title, manager_id, 0 AS depth, name AS path
    FROM employees WHERE manager_id IS NULL                       -- anchor member
    UNION ALL
    SELECT e.employee_id, e.name, e.title, e.manager_id, org.depth + 1,
           org.path || ' > ' || e.name
    FROM employees e JOIN org ON e.manager_id = org.employee_id   -- recursive member
)
SELECT substr('          ', 1, depth * 2) || name AS indented_name, title, depth, path
FROM org
ORDER BY path;

-- Q39: RECURSIVE CTE - category tree rolled up: revenue for a root category incl. all descendants
WITH RECURSIVE tree AS (
    SELECT category_id, name, category_id AS root_id, name AS root_name
    FROM categories WHERE parent_id IS NULL
    UNION ALL
    SELECT c.category_id, c.name, t.root_id, t.root_name
    FROM categories c JOIN tree t ON c.parent_id = t.category_id
)
SELECT t.root_name AS top_level_category,
       COUNT(DISTINCT p.product_id) AS products,
       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS revenue
FROM tree t
JOIN products p     ON p.category_id = t.category_id
JOIN order_items oi ON oi.product_id = p.product_id
JOIN orders o       ON o.order_id = oi.order_id AND o.status = 'completed'
GROUP BY t.root_name
ORDER BY revenue DESC;

-- Q40: RECURSIVE CTE - generate a calendar (date spine) to expose months with zero sales
WITH RECURSIVE months(m) AS (
    SELECT date('2024-01-01')
    UNION ALL
    SELECT date(m, '+1 month') FROM months WHERE m < date('2025-12-01')
),
monthly AS (
    SELECT strftime('%Y-%m', o.order_date) AS month,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
    FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status = 'completed'
    GROUP BY month
)
SELECT strftime('%Y-%m', m) AS month, ROUND(COALESCE(mo.revenue, 0), 2) AS revenue
FROM months
LEFT JOIN monthly mo ON mo.month = strftime('%Y-%m', m)
ORDER BY month
LIMIT 6;

-- Q41: RECURSIVE CTE - referral chain depth: who sits at the bottom of the longest referral chain
WITH RECURSIVE chain AS (
    SELECT customer_id, name, referred_by, 0 AS depth, CAST(customer_id AS TEXT) AS trail
    FROM customers WHERE referred_by IS NULL
    UNION ALL
    SELECT c.customer_id, c.name, c.referred_by, chain.depth + 1, chain.trail || '>' || c.customer_id
    FROM customers c JOIN chain ON c.referred_by = chain.customer_id
)
SELECT depth, COUNT(*) AS customers_at_depth, MAX(trail) AS example_trail
FROM chain
GROUP BY depth
ORDER BY depth;
