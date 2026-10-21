
-- #####################################################################
-- SECTION A: SELECT BASICS & DISTINCT
-- #####################################################################

-- Q1. All customers
SELECT * FROM customers;

-- Q2. Selected columns with aliases and a computed full name
SELECT customer_id,
       first_name || ' ' || last_name AS full_name,
       email AS contact_email
FROM customers;

-- Q3. Distinct countries our customers live in
SELECT DISTINCT country FROM customers ORDER BY country;

-- Q4. Distinct city + country combinations
SELECT DISTINCT city, country FROM customers ORDER BY country, city;

-- Q5. Distinct payment methods used on orders
SELECT DISTINCT payment_method FROM orders ORDER BY payment_method;

-- Q6. Distinct order statuses
SELECT DISTINCT status FROM orders;

-- Q7. Product name, price and profit margin per unit
SELECT name, price, cost, (price - cost) AS profit_per_unit
FROM products;

-- Q8. Margin percentage rounded to 1 decimal
SELECT name,
       ROUND((price - cost) / price * 100, 1) AS margin_pct
FROM products
ORDER BY margin_pct DESC;


-- #####################################################################
-- SECTION B: WHERE WITH OPERATORS, IN, BETWEEN, LIKE / ILIKE
-- #####################################################################

-- Q9. Products priced above 5,000
SELECT name, price FROM products WHERE price > 5000;

-- Q10. Products between 1,000 and 5,000 (BETWEEN is inclusive)
SELECT name, price FROM products WHERE price BETWEEN 1000 AND 5000;

-- Q11. Products in categories Smartphones(6), Laptops(7), Headphones(8)
SELECT name, category_id FROM products WHERE category_id IN (6, 7, 8);

-- Q12. Orders that are NOT cancelled or returned
SELECT order_id, status FROM orders
WHERE status NOT IN ('cancelled', 'returned');

-- Q13. Customers whose first name starts with 'A' (LIKE is case-sensitive)
SELECT first_name, last_name FROM customers WHERE first_name LIKE 'A%';

-- Q14. Products with 'sony' anywhere in name (ILIKE ignores case)
SELECT name FROM products WHERE name ILIKE '%sony%';

-- Q15. Products whose name ends with 'shirt' (case-insensitive)
SELECT name FROM products WHERE name ILIKE '%shirt';

-- Q16. Customers with exactly 5-letter first names (_ matches one character)
SELECT first_name FROM customers WHERE first_name LIKE '_____';

-- Q17. Customers with a .co.uk email
SELECT first_name, email FROM customers WHERE email LIKE '%.co.uk';

-- Q18. Customers with NO phone number recorded
SELECT first_name, last_name FROM customers WHERE phone IS NULL;

-- Q19. Customers who DO have a phone number
SELECT COUNT(*) AS with_phone FROM customers WHERE phone IS NOT NULL;

-- Q20. Combining AND / OR: cheap OR out-of-stock products
SELECT name, price, stock_qty
FROM products
WHERE price < 1000 OR stock_qty = 0;

-- Q21. AND with parentheses: Mumbai or Delhi customers who are active
SELECT first_name, city, is_active
FROM customers
WHERE city IN ('Mumbai', 'Delhi') AND is_active = TRUE;

-- Q22. NOT operator: products not available for sale
SELECT name FROM products WHERE NOT is_available;

-- Q23. Orders placed in Q1 2026 (Jan-Mar)
SELECT order_id, order_date, status
FROM orders
WHERE order_date >= '2026-01-01' AND order_date < '2026-04-01';

-- Q24. Orders between two dates using BETWEEN
SELECT order_id, order_date FROM orders
WHERE order_date BETWEEN '2026-03-01' AND '2026-03-31 23:59:59';

-- Q25. Not-equal operators (<> and !=) : orders not paid via UPI
SELECT order_id, payment_method FROM orders WHERE payment_method <> 'UPI';

-- Q26. Reviews with no comment text
SELECT review_id, rating FROM reviews WHERE comment IS NULL;

-- Q27. Reviews whose comment mentions "return" (case-insensitive)
SELECT review_id, comment FROM reviews WHERE comment ILIKE '%return%';


-- #####################################################################
-- SECTION C: ORDER BY, LIMIT, OFFSET
-- #####################################################################

-- Q28. Top 5 most expensive products
SELECT name, price FROM products ORDER BY price DESC LIMIT 5;

-- Q29. 5 cheapest products
SELECT name, price FROM products ORDER BY price ASC LIMIT 5;

-- Q30. Sort by two columns: category, then price high-to-low
SELECT category_id, name, price FROM products
ORDER BY category_id ASC, price DESC;

-- Q31. Customers ordered by loyalty points, highest first
SELECT first_name, loyalty_points FROM customers ORDER BY loyalty_points DESC;

-- Q32. Pagination: page 2 of products with 5 rows per page
SELECT product_id, name FROM products ORDER BY product_id LIMIT 5 OFFSET 5;

-- Q33. 5 most recent orders
SELECT order_id, order_date, status FROM orders ORDER BY order_date DESC LIMIT 5;

-- Q34. Order by an expression: biggest profit per unit first
SELECT name, (price - cost) AS profit FROM products ORDER BY (price - cost) DESC LIMIT 5;

-- Q35. NULL handling in sort: phone numbers, NULLs last
SELECT first_name, phone FROM customers ORDER BY phone NULLS LAST;


-- #####################################################################
-- SECTION D: AGGREGATE FUNCTIONS, GROUP BY, HAVING
-- #####################################################################

-- Q36. How many customers?
SELECT COUNT(*) AS total_customers FROM customers;

-- Q37. COUNT(*) vs COUNT(column): COUNT(column) skips NULLs
SELECT COUNT(*) AS all_rows, COUNT(phone) AS with_phone FROM customers;

-- Q38. Number of distinct cities
SELECT COUNT(DISTINCT city) AS unique_cities FROM customers;

-- Q39. Total revenue from delivered orders
SELECT SUM(total_amount) AS delivered_revenue FROM orders WHERE status = 'delivered';

-- Q40. Average, min and max product price
SELECT ROUND(AVG(price), 2) AS avg_price,
       MIN(price) AS cheapest,
       MAX(price) AS priciest
FROM products;

-- Q41. Customers per country
SELECT country, COUNT(*) AS customers
FROM customers GROUP BY country ORDER BY customers DESC;

-- Q42. Orders and revenue per status
SELECT status, COUNT(*) AS orders, SUM(total_amount) AS revenue
FROM orders GROUP BY status ORDER BY revenue DESC;

-- Q43. Products per category with average price
SELECT c.name AS category, COUNT(*) AS products, ROUND(AVG(p.price), 2) AS avg_price
FROM products p
JOIN categories c ON c.category_id = p.category_id
GROUP BY c.name
ORDER BY products DESC;

-- Q44. HAVING: categories with more than 3 products
SELECT category_id, COUNT(*) AS products
FROM products GROUP BY category_id HAVING COUNT(*) > 3;

-- Q45. HAVING: customers who placed 2 or more orders
SELECT customer_id, COUNT(*) AS orders_placed
FROM orders GROUP BY customer_id HAVING COUNT(*) >= 2
ORDER BY orders_placed DESC;

-- Q46. Monthly revenue (excluding cancelled orders)
SELECT DATE_TRUNC('month', order_date)::date AS month,
       SUM(total_amount) AS revenue
FROM orders
WHERE status <> 'cancelled'
GROUP BY 1 ORDER BY 1;

-- Q47. Payment method popularity
SELECT payment_method, COUNT(*) AS uses
FROM orders GROUP BY payment_method ORDER BY uses DESC;

-- Q48. Total inventory value (stock x cost)
SELECT SUM(stock_qty * cost) AS inventory_value_at_cost FROM products;

-- Q49. Average rating and review count per product (only reviewed ones)
SELECT product_id, ROUND(AVG(rating), 2) AS avg_rating, COUNT(*) AS reviews
FROM reviews GROUP BY product_id ORDER BY avg_rating DESC;

-- Q50. Total units sold per product (best sellers first)
SELECT p.name, SUM(oi.quantity) AS units_sold
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.name
ORDER BY units_sold DESC
LIMIT 5;


-- #####################################################################
-- SECTION E: JOINS, SUBQUERIES, CTEs, CASE, WINDOW FUNCTIONS
-- #####################################################################

-- Q51. INNER JOIN: each order with the customer name
SELECT o.order_id, c.first_name, c.last_name, o.status, o.total_amount
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
ORDER BY o.order_id;

-- Q52. Full order detail across 4 tables
SELECT o.order_id, c.first_name, p.name AS product, oi.quantity,
       oi.unit_price, (oi.quantity * oi.unit_price) AS line_total
FROM orders o
JOIN customers   c  ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id   = o.order_id
JOIN products    p  ON p.product_id  = oi.product_id
ORDER BY o.order_id, p.name;

-- Q53. LEFT JOIN anti-pattern: customers who never ordered
SELECT c.customer_id, c.first_name, c.last_name
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
WHERE o.order_id IS NULL;

-- Q54. Products that have never been ordered
SELECT p.product_id, p.name
FROM products p
LEFT JOIN order_items oi ON oi.product_id = p.product_id
WHERE oi.order_item_id IS NULL;

-- Q55. Subquery: products priced above the overall average
SELECT name, price FROM products
WHERE price > (SELECT AVG(price) FROM products)
ORDER BY price DESC;

-- Q56. Self join: category with its parent category name
SELECT c.name AS category, COALESCE(p.name, '(top level)') AS parent
FROM categories c
LEFT JOIN categories p ON p.category_id = c.parent_id
ORDER BY parent, category;

-- Q57. CTE: top 5 customers by lifetime spend (non-cancelled orders)
WITH spend AS (
    SELECT customer_id, SUM(total_amount) AS total_spent, COUNT(*) AS orders_placed
    FROM orders
    WHERE status NOT IN ('cancelled', 'returned')
    GROUP BY customer_id
)
SELECT c.first_name, c.last_name, s.orders_placed, s.total_spent
FROM spend s
JOIN customers c ON c.customer_id = s.customer_id
ORDER BY s.total_spent DESC
LIMIT 5;

-- Q58. EXISTS: customers who have written at least one review
SELECT c.first_name, c.last_name
FROM customers c
WHERE EXISTS (SELECT 1 FROM reviews r WHERE r.customer_id = c.customer_id);

-- Q59. CASE: label products by price tier
SELECT name, price,
       CASE
           WHEN price >= 50000 THEN 'Premium'
           WHEN price >= 5000  THEN 'Mid-range'
           WHEN price >= 1000  THEN 'Budget'
           ELSE 'Low-cost'
       END AS price_tier
FROM products
ORDER BY price DESC;

-- Q60. COALESCE: show 'N/A' where phone is missing
SELECT first_name, COALESCE(phone, 'N/A') AS phone FROM customers;

-- Q61. Window function: rank products by price inside each category
SELECT c.name AS category, p.name AS product, p.price,
       RANK() OVER (PARTITION BY p.category_id ORDER BY p.price DESC) AS price_rank
FROM products p
JOIN categories c ON c.category_id = p.category_id
ORDER BY c.name, price_rank;

-- Q62. Highly rated products: average >= 4 with at least 2 reviews
SELECT p.name, ROUND(AVG(r.rating), 2) AS avg_rating, COUNT(*) AS reviews
FROM reviews r
JOIN products p ON p.product_id = r.product_id
GROUP BY p.name
HAVING AVG(r.rating) >= 4 AND COUNT(*) >= 2;

-- Q63. Revenue by category (using order line items, excluding cancelled/returned)
SELECT c.name AS category, SUM(oi.quantity * oi.unit_price) AS revenue
FROM order_items oi
JOIN orders     o ON o.order_id    = oi.order_id
JOIN products   p ON p.product_id  = oi.product_id
JOIN categories c ON c.category_id = p.category_id
WHERE o.status NOT IN ('cancelled', 'returned')
GROUP BY c.name
ORDER BY revenue DESC;

-- Q64. Running total of revenue by order date (window function)
SELECT order_id, order_date::date AS day, total_amount,
       SUM(total_amount) OVER (ORDER BY order_date) AS running_total
FROM orders
WHERE status <> 'cancelled'
ORDER BY order_date;

-- Q65. Average order value per customer, highest first
SELECT c.first_name, ROUND(AVG(o.total_amount), 2) AS avg_order_value
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
GROUP BY c.first_name
ORDER BY avg_order_value DESC
LIMIT 5;

-- Q66. Low stock alert: available products with fewer than 20 units
SELECT sku, name, stock_qty FROM products
WHERE stock_qty < 20 AND is_available ORDER BY stock_qty;

-- Q67. Open orders (uses the partial index idx_orders_open)
SELECT order_id, customer_id, status, order_date
FROM orders WHERE status IN ('pending', 'processing') ORDER BY order_date;

-- Q68. EXPLAIN: see how PostgreSQL plans a query (index vs sequential scan)
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 1;
