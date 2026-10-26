-- Run this in pgAdmin: Query Tool on the database "etl_source"
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id    INT PRIMARY KEY,
    customer_name  VARCHAR(100),
    email          VARCHAR(150),
    city           VARCHAR(100),
    updated_at     TIMESTAMP DEFAULT NOW()
);

CREATE TABLE orders (
    order_id     INT PRIMARY KEY,
    customer_id  INT REFERENCES customers(customer_id),
    order_date   DATE,
    status       VARCHAR(30),
    updated_at   TIMESTAMP DEFAULT NOW()
);

-- Intentionally messy data (extra spaces, mixed case) to show the cleaning step
INSERT INTO customers (customer_id, customer_name, email, city, updated_at) VALUES
(1, '  alice johnson', 'Alice.Johnson@Example.com ', 'mumbai',    '2026-09-01 10:00:00'),
(2, 'BOB SMITH',       'bob.smith@example.com',      'pune',      '2026-09-01 10:00:00'),
(3, 'carol white',     'carol.white@example.com ',   'Delhi',     '2026-09-01 10:00:00'),
(4, 'David Lee',       'david.lee@example.com',      'bengaluru', '2026-09-01 10:00:00'),
(5, 'eva Brown ',      'eva.brown@example.com',      'MUMBAI',    '2026-09-01 10:00:00'),
(6, 'Frank Green',     'frank.green@example.com',    'Chennai',   '2026-09-01 10:00:00'),
(7, 'grace hall',      'grace.hall@example.com',     'pune',      '2026-09-01 10:00:00'),
(8, 'Henry Adams',     'henry.adams@example.com ',   'Hyderabad', '2026-09-01 10:00:00');

INSERT INTO orders (order_id, customer_id, order_date, status) VALUES
(1001, 1, '2026-09-05', 'completed'),
(1002, 2, '2026-09-07', 'Completed'),
(1003, 3, '2026-09-10', 'shipped'),
(1004, 1, '2026-09-12', 'COMPLETED'),
(1005, 4, '2026-09-15', ' pending'),
(1006, 5, '2026-09-18', 'cancelled'),
(1007, 6, '2026-09-20', 'completed'),
(1008, 2, '2026-09-25', 'shipped '),
(1009, 7, '2026-10-01', 'completed'),
(1010, 8, '2026-10-05', 'pending'),
(1011, 3, '2026-10-10', 'completed'),
(1012, 5, '2026-10-15', 'shipped');

UPDATE orders SET updated_at = order_date::timestamp + INTERVAL '12 hours';

SELECT * FROM customers;
SELECT * FROM orders;
