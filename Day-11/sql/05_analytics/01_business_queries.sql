-- Q1. Total sales, profit and margin overall
SELECT SUM(sales_amount)  AS total_sales,
       SUM(profit_amount) AS total_profit,
       ROUND(100.0 * SUM(profit_amount) / SUM(sales_amount), 1) AS profit_margin_pct
FROM   dw.fact_sales;

-- Q2. Sales by month (uses dim_date)
SELECT d.year, d.month_number, d.month_name,
       SUM(f.sales_amount) AS total_sales
FROM   dw.fact_sales f
JOIN   dw.dim_date d ON d.date_key = f.date_key
GROUP  BY d.year, d.month_number, d.month_name
ORDER  BY d.year, d.month_number;

-- Q3. Sales and profit by product category (uses dim_product)
SELECT p.category,
       SUM(f.quantity)      AS units_sold,
       SUM(f.sales_amount)  AS total_sales,
       SUM(f.profit_amount) AS total_profit
FROM   dw.fact_sales f
JOIN   dw.dim_product p ON p.product_key = f.product_key
GROUP  BY p.category
ORDER  BY total_sales DESC;

-- Q4. Sales by store region (uses dim_store)
SELECT s.region, s.store_name, SUM(f.sales_amount) AS total_sales
FROM   dw.fact_sales f
JOIN   dw.dim_store s ON s.store_key = f.store_key
GROUP  BY s.region, s.store_name
ORDER  BY total_sales DESC;

-- Q5. Top 5 customers by sales (uses dim_customer)
SELECT c.customer_id, c.full_name, c.segment, SUM(f.sales_amount) AS total_sales
FROM   dw.fact_sales f
JOIN   dw.dim_customer c ON c.customer_key = f.customer_key
GROUP  BY c.customer_id, c.full_name, c.segment
ORDER  BY total_sales DESC
LIMIT  5;

-- Q6. Quarter x category cross-tab (drill down: year > quarter > category)
SELECT d.year, d.quarter, p.category, SUM(f.sales_amount) AS total_sales
FROM   dw.fact_sales f
JOIN   dw.dim_date    d ON d.date_key    = f.date_key
JOIN   dw.dim_product p ON p.product_key = f.product_key
GROUP  BY ROLLUP (d.year, d.quarter, p.category)      -- adds subtotals & grand total
ORDER  BY d.year, d.quarter, p.category;

-- Q7. Running total of sales by month (window function)
SELECT month_name, monthly_sales,
       SUM(monthly_sales) OVER (ORDER BY month_number) AS running_total
FROM (
    SELECT d.month_number, d.month_name, SUM(f.sales_amount) AS monthly_sales
    FROM   dw.fact_sales f JOIN dw.dim_date d ON d.date_key = f.date_key
    GROUP  BY d.month_number, d.month_name
) m
ORDER BY month_number;

-- Q8. SNOWFLAKE vs STAR: same answer as Q3, but 3 joins instead of 1
SELECT c.category_name, SUM(f.sales_amount) AS total_sales
FROM   dw_snowflake.fact_sales f
JOIN   dw_snowflake.dim_product     p  ON p.product_key     = f.product_key
JOIN   dw_snowflake.dim_subcategory sc ON sc.subcategory_key = p.subcategory_key
JOIN   dw_snowflake.dim_category    c  ON c.category_key    = sc.category_key
GROUP  BY c.category_name
ORDER  BY total_sales DESC;

-- Q9. GALAXY: drill ACROSS two facts through conformed dims
--     (sales vs closing stock per category per month)
WITH sales AS (
    SELECT d.month_number, p.category, SUM(f.sales_amount) AS sales
    FROM dw.fact_sales f JOIN dw.dim_date d ON d.date_key=f.date_key
                         JOIN dw.dim_product p ON p.product_key=f.product_key
    GROUP BY 1,2),
stock AS (
    SELECT d.month_number, p.category, SUM(i.quantity_on_hand) AS units_in_stock
    FROM dw.fact_inventory i JOIN dw.dim_date d ON d.date_key=i.date_key
                             JOIN dw.dim_product p ON p.product_key=i.product_key
    GROUP BY 1,2)
SELECT st.month_number, st.category, COALESCE(sa.sales,0) AS sales, st.units_in_stock
FROM   stock st LEFT JOIN sales sa USING (month_number, category)
WHERE  st.month_number <= 2
ORDER  BY st.month_number, st.category;
