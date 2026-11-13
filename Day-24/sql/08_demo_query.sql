USE DATABASE {{DB}};
SELECT customer_id, city, segment, effective_date, end_date, is_current
FROM DW.dim_customer WHERE customer_id IN ('C0001','C0002') ORDER BY customer_id, effective_date;
