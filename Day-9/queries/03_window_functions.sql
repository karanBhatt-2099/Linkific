-- Q11: GROUP BY - Revenue per category
SELECT cat.name AS category,
       SUM(oi.quantity) AS units,
       SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN categories cat ON p.category_id = cat.category_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'completed'
GROUP BY cat.name;

-- Q12: HAVING - Customers with more than 10 orders
SELECT customer_id, COUNT(*) AS total_orders
FROM orders
WHERE status = 'completed'
GROUP BY customer_id
HAVING COUNT(*) > 10;

-- Q13: Multiple aggregations - Product sales
SELECT p.name,
       COUNT(*) AS total_items,
       SUM(oi.quantity) AS total_units,
       AVG(oi.discount) AS avg_discount,
       MIN(oi.discount) AS min_discount,
       MAX(oi.discount) AS max_discount
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.name;

-- Q14: COUNT DISTINCT - Unique customers
SELECT COUNT(DISTINCT customer_id) AS unique_customers
FROM orders
WHERE status = 'completed';

-- Q15: Conditional aggregation - Orders by status
SELECT
    COUNT(*) AS total_orders,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
    SUM(CASE WHEN status = 'returned' THEN 1 ELSE 0 END) AS returned
FROM orders;

-- Q16: HAVING - Products with above-average discounts
SELECT p.name, AVG(oi.discount) AS avg_discount
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.name
HAVING AVG(oi.discount) > (
    SELECT AVG(discount)
    FROM order_items
);

-- Q17: ROLLUP - Revenue per region and grand total
SELECT r.region_name,
       SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
JOIN regions r ON c.region_id = r.region_id
WHERE o.status = 'completed'
GROUP BY r.region_name;

-- Q18: CUBE - Revenue per region and category
SELECT r.region_name,
       cat.name AS category,
       SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
JOIN regions r ON c.region_id = r.region_id
JOIN products p ON oi.product_id = p.product_id
JOIN categories cat ON p.category_id = cat.category_id
WHERE o.status = 'completed'
GROUP BY r.region_name, cat.name;