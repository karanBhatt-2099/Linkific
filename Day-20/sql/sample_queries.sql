-- Paste into pgAdmin Query Tool (connect to the matching database first)

-- ecommerce_db: top 10 customers by spend
SELECT c.customer_id, c.first_name, c.last_name, SUM(o.total_amount) AS spent
FROM orders o JOIN customers c USING(customer_id)
WHERE o.status = 'delivered'
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY spent DESC LIMIT 10;

-- hr_db: average salary and headcount per department
SELECT d.name, COUNT(*) AS employees, ROUND(AVG(e.salary)) AS avg_salary
FROM employees e JOIN departments d USING(dept_id)
GROUP BY d.name ORDER BY avg_salary DESC;

-- finance_db: monthly transaction volume
SELECT DATE_TRUNC('month', txn_date) AS month, direction, SUM(amount) AS total
FROM transactions GROUP BY 1, 2 ORDER BY 1, 2;
