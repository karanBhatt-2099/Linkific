TRUNCATE dw.fact_sales RESTART IDENTITY;

INSERT INTO dw.fact_sales
    (date_key, customer_key, product_key, store_key,
     order_id, order_line_number,
     quantity, unit_price, discount_amount,
     sales_amount, cost_amount, profit_amount)
SELECT
    d.date_key,
    c.customer_key,
    p.product_key,
    s.store_key,
    src.order_id,
    src.line_no,
    src.qty,
    p.unit_price,
    src.discount,
    src.qty * p.unit_price - src.discount                      AS sales_amount,
    src.qty * p.unit_cost                                      AS cost_amount,
    (src.qty * p.unit_price - src.discount) - src.qty * p.unit_cost AS profit_amount
FROM (VALUES
    -- order_id, line_no, order_date,           customer, product, store, qty, discount
    ('O1001', 1, DATE '2026-01-05', 'C001', 'P001', 'S01', 1,  2000),
    ('O1001', 2, DATE '2026-01-05', 'C001', 'P002', 'S01', 1,     0),
    ('O1002', 1, DATE '2026-01-12', 'C002', 'P006', 'S02', 4,  1800),
    ('O1002', 2, DATE '2026-01-12', 'C002', 'P007', 'S02', 2,     0),
    ('O1003', 1, DATE '2026-01-20', 'C003', 'P004', 'S04', 1,  1000),
    ('O1004', 1, DATE '2026-02-02', 'C004', 'P009', 'S04', 10,    0),
    ('O1004', 2, DATE '2026-02-02', 'C004', 'P010', 'S04', 5,     0),
    ('O1005', 1, DATE '2026-02-09', 'C005', 'P001', 'S03', 3,  6000),
    ('O1005', 2, DATE '2026-02-09', 'C005', 'P003', 'S03', 3,     0),
    ('O1006', 1, DATE '2026-02-14', 'C006', 'P005', 'S02', 2,   500),
    ('O1007', 1, DATE '2026-02-25', 'C007', 'P012', 'S01', 1,     0),
    ('O1008', 1, DATE '2026-03-03', 'C008', 'P008', 'S04', 2,   300),
    ('O1008', 2, DATE '2026-03-03', 'C008', 'P011', 'S04', 2,     0),
    ('O1009', 1, DATE '2026-03-10', 'C001', 'P003', 'S01', 1,     0),
    ('O1010', 1, DATE '2026-03-18', 'C009', 'P001', 'S03', 2,  4000),
    ('O1010', 2, DATE '2026-03-18', 'C009', 'P005', 'S03', 2,     0),
    ('O1011', 1, DATE '2026-03-28', 'C010', 'P004', 'S03', 1,     0),
    ('O1012', 1, DATE '2026-04-06', 'C002', 'P007', 'S02', 1,     0),
    ('O1012', 2, DATE '2026-04-06', 'C002', 'P006', 'S02', 2,     0),
    ('O1013', 1, DATE '2026-04-15', 'C003', 'P002', 'S04', 2,     0),
    ('O1013', 2, DATE '2026-04-15', 'C003', 'P009', 'S04', 4,     0),
    ('O1014', 1, DATE '2026-04-22', 'C007', 'P012', 'S01', 2,  1000),
    ('O1015', 1, DATE '2026-05-04', 'C005', 'P004', 'S02', 2,  2000),
    ('O1016', 1, DATE '2026-05-19', 'C010', 'P011', 'S03', 3,     0),
    ('O1016', 2, DATE '2026-05-19', 'C010', 'P008', 'S03', 1,     0),
    ('O1017', 1, DATE '2026-06-02', 'C004', 'P005', 'S04', 1,     0),
    ('O1018', 1, DATE '2026-06-16', 'C006', 'P006', 'S01', 1,   500)
) AS src(order_id, line_no, order_date, customer_id, product_id, store_id, qty, discount)
JOIN dw.dim_date     d ON d.full_date   = src.order_date
JOIN dw.dim_customer c ON c.customer_id = src.customer_id AND c.is_current   -- current version
JOIN dw.dim_product  p ON p.product_id  = src.product_id
JOIN dw.dim_store    s ON s.store_id    = src.store_id;

-- Validation: expect 27 rows loaded, total sales_amount shown below
SELECT COUNT(*) AS fact_rows, SUM(sales_amount) AS total_sales, SUM(profit_amount) AS total_profit
FROM dw.fact_sales;
