DROP TABLE IF EXISTS scd_demo.customer_scd3 CASCADE;

CREATE TABLE scd_demo.customer_scd3 (
    customer_key      INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id       VARCHAR(10)  NOT NULL UNIQUE,
    full_name         VARCHAR(100) NOT NULL,
    current_city      VARCHAR(50),
    previous_city     VARCHAR(50),         -- NULL until the first change
    city_changed_date DATE
);

INSERT INTO scd_demo.customer_scd3 (customer_id, full_name, current_city) VALUES
('C001', 'Aarav Sharma', 'Mumbai'),
('C002', 'Priya Patel',  'Ahmedabad');

-- CHANGE #1 : Priya moves Ahmedabad -> Surat (2026-06-01)
-- Order inside UPDATE does not matter: PostgreSQL evaluates every right-hand
-- side using the OLD row, so previous_city = current_city copies the old value.
UPDATE scd_demo.customer_scd3
SET    previous_city     = current_city,
       current_city      = 'Surat',
       city_changed_date = DATE '2026-06-01'
WHERE  customer_id = 'C002'
  AND  current_city IS DISTINCT FROM 'Surat';

SELECT customer_id, current_city, previous_city, city_changed_date
FROM   scd_demo.customer_scd3 ORDER BY customer_id;
-- EXPECTED:
--  C001 | Mumbai | NULL      | NULL
--  C002 | Surat  | Ahmedabad | 2026-06-01

-- CHANGE #2 : Priya moves again Surat -> Vadodara (2026-09-01)
UPDATE scd_demo.customer_scd3
SET    previous_city     = current_city,
       current_city      = 'Vadodara',
       city_changed_date = DATE '2026-09-01'
WHERE  customer_id = 'C002'
  AND  current_city IS DISTINCT FROM 'Vadodara';

SELECT customer_id, current_city, previous_city, city_changed_date
FROM   scd_demo.customer_scd3 ORDER BY customer_id;
-- EXPECTED:
--  C001 | Mumbai   | NULL  | NULL
--  C002 | Vadodara | Surat | 2026-09-01     <- 'Ahmedabad' is LOST (the Type 3 limitation)

-- VALIDATION: Priya must show Vadodara / Surat
SELECT (current_city = 'Vadodara' AND previous_city = 'Surat') AS type3_works
FROM   scd_demo.customer_scd3 WHERE customer_id = 'C002';
