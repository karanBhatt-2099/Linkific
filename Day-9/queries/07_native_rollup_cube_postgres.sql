
SELECT COALESCE(r.region_name, 'ALL REGIONS')           AS region,
       COALESCE(EXTRACT(YEAR FROM o.order_date)::text, 'ALL YEARS') AS year,
       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount))::numeric, 2) AS revenue,
       GROUPING(r.region_name, EXTRACT(YEAR FROM o.order_date)) AS grouping_level  -- 0 detail, 1/2/3 subtotals
FROM order_items oi
JOIN orders o    ON o.order_id = oi.order_id AND o.status = 'completed'
JOIN customers c ON c.customer_id = o.customer_id
JOIN regions r   ON r.region_id = c.region_id
GROUP BY ROLLUP (r.region_name, EXTRACT(YEAR FROM o.order_date))
ORDER BY 1, 2;

-- CUBE: all 2^n combinations of (region, category)
SELECT COALESCE(r.region_name, '*') AS region, COALESCE(cat.name, '*') AS category,
       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount))::numeric, 2) AS revenue
FROM order_items oi
JOIN orders o       ON o.order_id = oi.order_id AND o.status = 'completed'
JOIN customers c    ON c.customer_id = o.customer_id
JOIN regions r      ON r.region_id = c.region_id
JOIN products p     ON p.product_id = oi.product_id
JOIN categories cat ON cat.category_id = p.category_id
GROUP BY CUBE (r.region_name, cat.name)
ORDER BY 1, 2;

-- GROUPING SETS: pick exactly the combinations you want
SELECT r.region_name, cat.name AS category, SUM(oi.quantity) AS units
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
JOIN customers c ON c.customer_id = o.customer_id
JOIN regions r ON r.region_id = c.region_id
JOIN products p ON p.product_id = oi.product_id
JOIN categories cat ON cat.category_id = p.category_id
GROUP BY GROUPING SETS ((r.region_name), (cat.name), ());
