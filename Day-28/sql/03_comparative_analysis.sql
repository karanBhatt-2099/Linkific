-- ============================================
-- 03. COMPARATIVE ANALYSIS
-- ============================================

-- 3.1 Year-over-year revenue by quarter (2023 vs 2024)
SELECT
    d.quarter,
    ROUND(SUM(CASE WHEN d.year = 2023 THEN f.revenue ELSE 0 END), 2) AS revenue_2023,
    ROUND(SUM(CASE WHEN d.year = 2024 THEN f.revenue ELSE 0 END), 2) AS revenue_2024,
    ROUND((SUM(CASE WHEN d.year = 2024 THEN f.revenue ELSE 0 END)
         - SUM(CASE WHEN d.year = 2023 THEN f.revenue ELSE 0 END)) * 100.0
         / SUM(CASE WHEN d.year = 2023 THEN f.revenue ELSE 0 END), 2) AS yoy_growth_pct
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.quarter
ORDER BY d.quarter;

-- 3.2 Region comparison
SELECT
    c.region,
    ROUND(SUM(f.revenue), 2)          AS revenue,
    ROUND(SUM(f.revenue - f.cost), 2) AS profit,
    COUNT(*)                          AS orders
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.region
ORDER BY revenue DESC;

-- 3.3 Segment vs average order value
SELECT
    c.segment,
    COUNT(*)                              AS orders,
    ROUND(AVG(f.revenue), 2)              AS avg_order_value,
    ROUND(SUM(f.revenue), 2)              AS revenue
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.segment
ORDER BY revenue DESC;

-- 3.4 Weekday vs weekend
SELECT
    CASE WHEN d.is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    ROUND(SUM(f.revenue), 2) AS revenue,
    ROUND(SUM(f.revenue) / COUNT(DISTINCT d.date_key), 2) AS revenue_per_day
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY day_type;
