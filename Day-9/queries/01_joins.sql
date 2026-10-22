-- Q01: INNER JOIN - Orders with customers
SELECT o.order_id, c.name
FROM orders o
INNER JOIN customers c
ON o.customer_id = c.customer_id;

-- Q02: LEFT JOIN - All customers and their orders
SELECT c.name, o.order_id
FROM customers c
LEFT JOIN orders o
ON c.customer_id = o.customer_id;

-- Q03: Customers who never ordered
SELECT c.name
FROM customers c
LEFT JOIN orders o
ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;

-- Q04: RIGHT JOIN - All products and their sales
SELECT p.name, oi.quantity
FROM order_items oi
RIGHT JOIN products p
ON oi.product_id = p.product_id;

-- Q05: FULL OUTER JOIN - All customers and regions
SELECT c.name, r.region_name
FROM customers c
FULL OUTER JOIN regions r
ON c.region_id = r.region_id;

-- Q06: CROSS JOIN - Every region with every category
SELECT r.region_name, cat.name AS category
FROM regions r
CROSS JOIN categories cat;

-- Q07: SELF JOIN - Employees and their managers
SELECT e.name AS employee, m.name AS manager
FROM employees e
LEFT JOIN employees m
ON e.manager_id = m.employee_id;

-- Q08: SELF JOIN - Customers and their referrers
SELECT c.name AS customer, ref.name AS referred_by
FROM customers c
JOIN customers ref
ON c.referred_by = ref.customer_id;

-- Q09: SELF JOIN - Products in the same category
SELECT a.name AS product1, b.name AS product2
FROM products a
JOIN products b
ON a.category_id = b.category_id
AND a.product_id < b.product_id;

-- Q10: MULTI-TABLE JOIN - Orders with customer and product
SELECT o.order_id, c.name AS customer, p.name AS product
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id;