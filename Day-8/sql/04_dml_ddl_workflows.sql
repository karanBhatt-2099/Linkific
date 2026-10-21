-- #####################################################################
-- PART 1: ALTER TABLE
-- #####################################################################
BEGIN;

ALTER TABLE products ADD COLUMN weight_kg NUMERIC(6,2);                    -- add column
ALTER TABLE products ALTER COLUMN weight_kg SET DEFAULT 0.5;               -- set default
ALTER TABLE products RENAME COLUMN weight_kg TO shipping_weight_kg;        -- rename column
ALTER TABLE products ALTER COLUMN shipping_weight_kg TYPE NUMERIC(8,3);    -- change type
ALTER TABLE products ADD CONSTRAINT chk_weight_positive
      CHECK (shipping_weight_kg IS NULL OR shipping_weight_kg > 0);        -- add constraint
ALTER TABLE products DROP CONSTRAINT chk_weight_positive;                  -- drop constraint
ALTER TABLE products DROP COLUMN shipping_weight_kg;                       -- drop column

ROLLBACK;  -- schema changes are transactional in PostgreSQL!


-- #####################################################################
-- PART 2: PRACTICE WITH A SCRATCH TABLE (CREATE -> DML -> DROP)
-- #####################################################################
DROP TABLE IF EXISTS wishlist;

CREATE TABLE wishlist (
    wishlist_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    product_id  INT NOT NULL REFERENCES products(product_id)   ON DELETE CASCADE,
    priority    SMALLINT NOT NULL DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
    added_on    DATE NOT NULL DEFAULT CURRENT_DATE,
    UNIQUE (customer_id, product_id)
);

-- Single-row INSERT with RETURNING (get the generated id back)
INSERT INTO wishlist (customer_id, product_id, priority)
VALUES (1, 3, 2)
RETURNING wishlist_id, customer_id, product_id;

-- Bulk INSERT (multiple rows in one statement)
INSERT INTO wishlist (customer_id, product_id, priority) VALUES
(1, 6, 1),
(2, 1, 1),
(2, 13, 4),
(5, 20, 3),
(8, 2, 2)
RETURNING *;

-- INSERT ... SELECT (copy rows from a query)
INSERT INTO wishlist (customer_id, product_id, priority)
SELECT 10, product_id, 5 FROM products WHERE category_id = 8
RETURNING *;

-- UPSERT: insert, or update if (customer_id, product_id) already exists
INSERT INTO wishlist (customer_id, product_id, priority)
VALUES (1, 3, 1)
ON CONFLICT (customer_id, product_id)
DO UPDATE SET priority = EXCLUDED.priority
RETURNING *;

-- UPDATE with WHERE + RETURNING
UPDATE wishlist SET priority = priority - 1
WHERE priority > 1 AND customer_id = 2
RETURNING *;

-- UPDATE using another table (FROM)
UPDATE wishlist w
SET priority = 1
FROM products p
WHERE p.product_id = w.product_id AND p.price > 50000
RETURNING w.wishlist_id, p.name, w.priority;

-- DELETE with WHERE + RETURNING
DELETE FROM wishlist WHERE priority = 5 RETURNING *;

-- Current state
SELECT * FROM wishlist ORDER BY wishlist_id;

-- Empty the table but keep the structure (also resets identity)
TRUNCATE TABLE wishlist RESTART IDENTITY;

-- DROP TABLE removes structure + data
DROP TABLE wishlist;


-- #####################################################################
-- PART 3: REAL-WORLD WORKFLOW — PLACE AN ORDER (transaction)
-- #####################################################################
BEGIN;

-- 3a. Create the order and its items in one go (CTE with INSERT ... RETURNING)
WITH new_order AS (
    INSERT INTO orders (customer_id, status, payment_method, shipping_city, shipping_country)
    VALUES (9, 'pending', 'UPI', 'Lucknow', 'India')
    RETURNING order_id
)
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT n.order_id, p.product_id, v.qty, p.price
FROM new_order n
CROSS JOIN (VALUES (14, 2), (15, 1)) AS v(product_id, qty)
JOIN products p ON p.product_id = v.product_id;

-- 3b. Reduce stock for the purchased products
UPDATE products p
SET stock_qty = p.stock_qty - v.qty
FROM (VALUES (14, 2), (15, 1)) AS v(product_id, qty)
WHERE p.product_id = v.product_id
RETURNING p.product_id, p.name, p.stock_qty;

-- 3c. Calculate the order total
UPDATE orders o
SET total_amount = (SELECT SUM(quantity * unit_price) FROM order_items WHERE order_id = o.order_id)
WHERE o.order_id = (SELECT MAX(order_id) FROM orders)
RETURNING order_id, customer_id, total_amount;

-- 3d. Award loyalty points: 1 point per 100 currency units spent
UPDATE customers
SET loyalty_points = loyalty_points + 14
WHERE customer_id = 9
RETURNING customer_id, first_name, loyalty_points;

ROLLBACK;  -- change to COMMIT; to keep this order


-- #####################################################################
-- PART 4: SAFE DELETE PATTERNS
-- #####################################################################
BEGIN;

-- Deleting an order automatically removes its items (ON DELETE CASCADE)
DELETE FROM orders WHERE order_id = 5 RETURNING order_id, status;
SELECT COUNT(*) AS items_left_for_order_5 FROM order_items WHERE order_id = 5;   -- 0

-- A product that has order history CANNOT be deleted (FK protects it).
-- Uncomment to see the error:
-- DELETE FROM products WHERE product_id = 1;
-- ERROR: update or delete on table "products" violates foreign key constraint

-- Soft-delete pattern: deactivate instead of delete
UPDATE customers SET is_active = FALSE WHERE customer_id = 9 RETURNING customer_id, is_active;

ROLLBACK;


-- #####################################################################
-- PART 5: CONSTRAINT VIOLATIONS (each should FAIL - uncomment one at a time)
-- #####################################################################
-- INSERT INTO customers (first_name,last_name,email) VALUES ('X','Y','aarav.sharma@example.com');  -- UNIQUE
-- INSERT INTO products (sku,name,category_id,price,cost) VALUES ('T-1','Test',1,-5,1);             -- CHECK (price rules)
-- INSERT INTO orders (customer_id,payment_method) VALUES (9999,'UPI');                             -- FOREIGN KEY
-- INSERT INTO reviews (product_id,customer_id,rating) VALUES (1,2,9);                              -- CHECK rating 1-5
-- INSERT INTO customers (first_name,last_name) VALUES ('NoEmail','User');                          -- NOT NULL
