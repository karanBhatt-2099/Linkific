-- ============================================
-- 02. TREND ANALYSIS
-- ============================================

-- 2.1 Monthly revenue
SELECT
    d.year,
    d.month,
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month
ORDER BY d.year, d.month;

-- 2.2 Month-over-month growth %
WITH monthly AS (
    SELECT d.year, d.month, SUM(f.revenue) AS revenue
    FROM fact_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    GROUP BY d.year, d.month
)
SELECT
    year,
    month,
    ROUND(revenue, 2) AS revenue,
    ROUND(LAG(revenue) OVER (ORDER BY year, month), 2) AS prev_month_revenue,
    ROUND((revenue - LAG(revenue) OVER (ORDER BY year, month)) * 100.0
          / LAG(revenue) OVER (ORDER BY year, month), 2) AS mom_growth_pct
FROM monthly
ORDER BY year, month;

-- 2.3 Running (cumulative) revenue
WITH monthly AS (
    SELECT d.year, d.month, SUM(f.revenue) AS revenue
    FROM fact_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    GROUP BY d.year, d.month
)
SELECT
    year,
    month,
    ROUND(revenue, 2) AS revenue,
    ROUND(SUM(revenue) OVER (ORDER BY year, month), 2) AS running_total
FROM monthly
ORDER BY year, month;
