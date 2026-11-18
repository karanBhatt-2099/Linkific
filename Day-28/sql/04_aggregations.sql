-- ============================================
-- 04. AGGREGATIONS & RANKINGS
-- ============================================

-- 4.1 Rank products inside each category
SELECT *
FROM (
    SELECT
        p.category,
        p.product_name,
        ROUND(SUM(f.revenue), 2) AS revenue,
        RANK() OVER (PARTITION BY p.category ORDER BY SUM(f.revenue) DESC) AS rank_in_category
    FROM fact_sales f
    JOIN dim_product p ON f.product_key = p.product_key
    GROUP BY p.category, p.product_name
)
WHERE rank_in_category <= 3
ORDER BY category, rank_in_category;

-- 4.2 Discount impact
SELECT
    discount,
    COUNT(*)                                       AS orders,
    ROUND(SUM(revenue), 2)                         AS revenue,
    ROUND(SUM(revenue - cost) * 100.0 / SUM(revenue), 2) AS margin_pct
FROM fact_sales
GROUP BY discount
ORDER BY discount;

-- 4.3 Category x Region revenue matrix
SELECT
    p.category,
    ROUND(SUM(CASE WHEN c.region = 'North' THEN f.revenue ELSE 0 END), 0) AS north,
    ROUND(SUM(CASE WHEN c.region = 'South' THEN f.revenue ELSE 0 END), 0) AS south,
    ROUND(SUM(CASE WHEN c.region = 'East'  THEN f.revenue ELSE 0 END), 0) AS east,
    ROUND(SUM(CASE WHEN c.region = 'West'  THEN f.revenue ELSE 0 END), 0) AS west
FROM fact_sales f
JOIN dim_product  p ON f.product_key  = p.product_key
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY p.category;

-- 4.4 Customers with above-average spend
WITH spend AS (
    SELECT customer_key, SUM(revenue) AS total_spend
    FROM fact_sales
    GROUP BY customer_key
)
SELECT COUNT(*) AS high_value_customers
FROM spend
WHERE total_spend > (SELECT AVG(total_spend) FROM spend);
