-- ============================================
-- 01. BUSINESS METRICS (KPIs)
-- ============================================

-- 1.1 Overall KPIs
SELECT
    ROUND(SUM(revenue), 2)                        AS total_revenue,
    ROUND(SUM(revenue - cost), 2)                 AS total_profit,
    ROUND(SUM(revenue - cost) * 100.0 / SUM(revenue), 2) AS profit_margin_pct,
    COUNT(*)                                      AS total_orders,
    SUM(quantity)                                 AS units_sold,
    ROUND(SUM(revenue) / COUNT(*), 2)             AS avg_order_value,
    COUNT(DISTINCT customer_key)                  AS active_customers
FROM fact_sales;

-- 1.2 Revenue and profit by category
SELECT
    p.category,
    ROUND(SUM(f.revenue), 2)             AS revenue,
    ROUND(SUM(f.revenue - f.cost), 2)    AS profit,
    ROUND(SUM(f.revenue - f.cost) * 100.0 / SUM(f.revenue), 2) AS margin_pct
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category
ORDER BY revenue DESC;

-- 1.3 Top 10 customers by revenue
SELECT
    c.customer_name,
    c.segment,
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.customer_name, c.segment
ORDER BY revenue DESC
LIMIT 10;
