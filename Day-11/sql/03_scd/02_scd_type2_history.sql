DROP TABLE IF EXISTS scd_demo.fact_orders_scd2 CASCADE;
DROP TABLE IF EXISTS scd_demo.customer_scd2    CASCADE;
DROP TABLE IF EXISTS scd_demo.stg_customer2    CASCADE;

CREATE TABLE scd_demo.customer_scd2 (
    customer_key   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- surrogate (per version)
    customer_id    VARCHAR(10)  NOT NULL,                            -- natural (same across versions)
    full_name      VARCHAR(100) NOT NULL,
    city           VARCHAR(50),
    effective_date DATE    NOT NULL,
    end_date       DATE    NOT NULL DEFAULT DATE '9999-12-31',       -- 9999-12-31 = "still open"
    is_current     BOOLEAN NOT NULL DEFAULT TRUE
);
-- At most ONE current row per customer (partial unique index):
CREATE UNIQUE INDEX uq_scd2_one_current ON scd_demo.customer_scd2 (customer_id) WHERE is_current;

-- STEP 1: initial load
INSERT INTO scd_demo.customer_scd2 (customer_id, full_name, city, effective_date) VALUES
('C001', 'Aarav Sharma', 'Mumbai',    DATE '2025-01-01'),
('C002', 'Priya Patel',  'Ahmedabad', DATE '2025-01-01');

-- STEP 2: staging data (the load date is fixed to 2026-06-01 so your output
--         matches this guide; in real ETL use CURRENT_DATE).
CREATE TABLE scd_demo.stg_customer2 (customer_id VARCHAR(10), full_name VARCHAR(100), city VARCHAR(50));
INSERT INTO scd_demo.stg_customer2 VALUES
('C001', 'Aarav Sharma', 'Pune'),        -- MOVED Mumbai -> Pune  => new version
('C002', 'Priya Patel',  'Ahmedabad'),   -- unchanged             => nothing
('C003', 'Rahul Verma',  'Delhi');       -- new customer          => first version

-- STEP 3: the SCD2 load, in ONE transaction (all-or-nothing)
BEGIN;

-- 3a) CLOSE the current row of every customer whose tracked attribute changed.
UPDATE scd_demo.customer_scd2 t
SET    end_date   = DATE '2026-06-01' - 1,     -- day before the change
       is_current = FALSE
FROM   scd_demo.stg_customer2 s
WHERE  t.customer_id = s.customer_id
  AND  t.is_current
  AND (t.city      IS DISTINCT FROM s.city
    OR t.full_name IS DISTINCT FROM s.full_name);

-- 3b) INSERT a new current row for every customer that now has NO current row
--     (= just-closed customers + brand-new customers).
INSERT INTO scd_demo.customer_scd2 (customer_id, full_name, city, effective_date)
SELECT s.customer_id, s.full_name, s.city, DATE '2026-06-01'
FROM   scd_demo.stg_customer2 s
WHERE  NOT EXISTS (SELECT 1 FROM scd_demo.customer_scd2 t
                   WHERE t.customer_id = s.customer_id AND t.is_current);

COMMIT;

-- STEP 4: look at the history
SELECT customer_key, customer_id, city, effective_date, end_date, is_current
FROM   scd_demo.customer_scd2
ORDER  BY customer_id, effective_date;
-- EXPECTED:
--  customer_key | customer_id | city      | effective_date | end_date   | is_current
--  1            | C001        | Mumbai    | 2025-01-01     | 2026-05-31 | f
--  3            | C001        | Pune      | 2026-06-01     | 9999-12-31 | t
--  2            | C002        | Ahmedabad | 2025-01-01     | 9999-12-31 | t
--  4            | C003        | Delhi     | 2026-06-01     | 9999-12-31 | t
-- (Aarav's NEW version got a NEW surrogate key (3); customer_id C001 stays.
--  If your key numbers differ slightly, that is fine - only the pattern matters.)

-- STEP 5: RE-RUN safety (idempotent). Running 3a+3b again changes nothing
-- because staging now equals the current rows. (Try it!)

-- STEP 6: WHY IT MATTERS - facts keep pointing to the version that was true
-- when the sale happened (point-in-time lookup by date range).
CREATE TABLE scd_demo.fact_orders_scd2 (
    order_id     VARCHAR(10) PRIMARY KEY,
    customer_key INTEGER NOT NULL REFERENCES scd_demo.customer_scd2(customer_key),
    order_date   DATE    NOT NULL,
    amount       NUMERIC(12,2) NOT NULL
);

INSERT INTO scd_demo.fact_orders_scd2 (order_id, customer_key, order_date, amount)
SELECT o.order_id, c.customer_key, o.order_date, o.amount
FROM (VALUES ('X1', 'C001', DATE '2026-03-10', 5000),    -- before the move
             ('X2', 'C001', DATE '2026-06-15', 7000),    -- after the move
             ('X3', 'C002', DATE '2026-06-20', 3000)
     ) AS o(order_id, customer_id, order_date, amount)
JOIN scd_demo.customer_scd2 c
  ON c.customer_id = o.customer_id
 AND o.order_date BETWEEN c.effective_date AND c.end_date;   -- the key trick

-- Sales by city: Aarav's March order is credited to MUMBAI, June order to PUNE.
SELECT c.city, SUM(f.amount) AS total_sales
FROM   scd_demo.fact_orders_scd2 f
JOIN   scd_demo.customer_scd2    c ON c.customer_key = f.customer_key
GROUP  BY c.city
ORDER  BY c.city;
-- EXPECTED:  Ahmedabad 3000 | Mumbai 5000 | Pune 7000
-- (With SCD Type 1 all 12000 for Aarav would show under Pune - history rewritten.)
