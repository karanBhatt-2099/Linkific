-- STEP 0: clean start (safe to re-run)
DROP TABLE IF EXISTS scd_demo.customer_scd1 CASCADE;
DROP TABLE IF EXISTS scd_demo.stg_customer  CASCADE;

CREATE TABLE scd_demo.customer_scd1 (
    customer_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id  VARCHAR(10) NOT NULL UNIQUE,
    full_name    VARCHAR(100) NOT NULL,
    email        VARCHAR(100),
    city         VARCHAR(50)
);

-- STEP 1: initial load (3 customers)
INSERT INTO scd_demo.customer_scd1 (customer_id, full_name, email, city) VALUES
('C001', 'Aarav Sharma', 'aarav.old@example.com',  'Mumbai'),
('C002', 'Priya Patel',  'priya.patel@example.com','Ahmedabad'),
('C003', 'Rahul Verma',  'rahul.verma@example.com','Delhi');

SELECT * FROM scd_demo.customer_scd1 ORDER BY customer_key;   -- BEFORE

-- STEP 2: a STAGING table = today's incoming data from the source system
CREATE TABLE scd_demo.stg_customer (
    customer_id VARCHAR(10), full_name VARCHAR(100), email VARCHAR(100), city VARCHAR(50)
);
INSERT INTO scd_demo.stg_customer VALUES
('C001', 'Aarav Sharma', 'aarav.sharma@example.com', 'Mumbai'),     -- email corrected
('C002', 'Priya Patel',  'priya.patel@example.com',   'Surat'),      -- city changed
('C003', 'Rahul Verma',  'rahul.verma@example.com',   'Delhi'),      -- unchanged
('C004', 'Sneha Iyer',   'sneha.iyer@example.com',    'Chennai');    -- brand new

-- STEP 3a: UPDATE existing customers whose attributes differ.
-- IS DISTINCT FROM is NULL-safe (a plain <> would miss NULL changes).
UPDATE scd_demo.customer_scd1 t
SET    full_name = s.full_name,
       email     = s.email,
       city      = s.city
FROM   scd_demo.stg_customer s
WHERE  t.customer_id = s.customer_id
  AND (t.full_name IS DISTINCT FROM s.full_name
    OR t.email     IS DISTINCT FROM s.email
    OR t.city      IS DISTINCT FROM s.city);

-- STEP 3b: INSERT customers that do not exist yet.
INSERT INTO scd_demo.customer_scd1 (customer_id, full_name, email, city)
SELECT s.customer_id, s.full_name, s.email, s.city
FROM   scd_demo.stg_customer s
WHERE  NOT EXISTS (SELECT 1 FROM scd_demo.customer_scd1 t WHERE t.customer_id = s.customer_id);

-- (Shortcut you can learn later: INSERT ... ON CONFLICT (customer_id) DO UPDATE ...)

-- STEP 4: AFTER  -> old email & old city are GONE.
SELECT * FROM scd_demo.customer_scd1 ORDER BY customer_key;
-- EXPECTED:
--  customer_key | customer_id | full_name    | email                    | city
--  1            | C001        | Aarav Sharma | aarav.sharma@example.com | Mumbai
--  2            | C002        | Priya Patel  | priya.patel@example.com  | Surat
--  3            | C003        | Rahul Verma  | rahul.verma@example.com  | Delhi
--  4            | C004        | Sneha Iyer   | sneha.iyer@example.com   | Chennai

-- VALIDATION: exactly 4 rows, one per customer_id, Priya now in Surat
SELECT COUNT(*) = 4 AS four_rows,
       COUNT(DISTINCT customer_id) = 4 AS no_duplicates,
       BOOL_OR(customer_id='C002' AND city='Surat') AS priya_in_surat
FROM scd_demo.customer_scd1;
