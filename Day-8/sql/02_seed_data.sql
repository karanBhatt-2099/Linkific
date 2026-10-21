-- CUSTOMERS (15) --------------------------------------------------------
INSERT INTO customers (first_name, last_name, email, phone, city, country, loyalty_points, is_active, created_at) VALUES
('Aarav',  'Sharma',   'aarav.sharma@example.com',  '9820011111', 'Mumbai',    'India',     1200, TRUE,  '2025-06-01 10:00+05:30'),
('Priya',  'Patel',    'priya.patel@example.com',   '9820022222', 'Ahmedabad', 'India',      800, TRUE,  '2025-06-15 11:30+05:30'),
('Rohan',  'Mehta',    'rohan.mehta@example.com',   '9820033333', 'Pune',      'India',      450, TRUE,  '2025-07-02 09:15+05:30'),
('Ananya', 'Iyer',     'ananya.iyer@example.com',   '9820044444', 'Chennai',   'India',      150, TRUE,  '2025-08-10 14:00+05:30'),
('Vikram', 'Singh',    'vikram.singh@example.com',  '9820055555', 'Delhi',     'India',     2100, TRUE,  '2025-08-22 16:45+05:30'),
('Sneha',  'Reddy',    'sneha.reddy@example.com',   '9820066666', 'Hyderabad', 'India',      600, TRUE,  '2025-09-05 12:00+05:30'),
('Arjun',  'Nair',     'arjun.nair@example.com',    '9820077777', 'Kochi',     'India',      300, TRUE,  '2025-09-18 08:30+05:30'),
('Kavya',  'Menon',    'kavya.menon@example.com',   '9820088888', 'Bengaluru', 'India',     1750, TRUE,  '2025-10-01 19:00+05:30'),
('Rahul',  'Verma',    'rahul.verma@example.com',   NULL,         'Lucknow',   'India',        0, TRUE,  '2025-10-20 13:20+05:30'),
('Isha',   'Gupta',    'isha.gupta@example.com',    '9820099999', 'Mumbai',    'India',      950, TRUE,  '2025-11-03 10:10+05:30'),
('John',   'Smith',    'john.smith@example.co.uk',  '447700900001','London',   'UK',         500, TRUE,  '2025-11-15 15:00+00:00'),
('Emily',  'Johnson',  'emily.johnson@example.com', '12125550123','New York',  'USA',        700, TRUE,  '2025-12-01 17:30-05:00'),
('Liam',   'Chen',     'liam.chen@example.com',     '6591234567', 'Singapore', 'Singapore',  250, TRUE,  '2025-12-12 11:11+08:00'),
('Sara',   'Khan',     'sara.khan@example.com',     '9820012345', 'Delhi',     'India',       50, FALSE, '2026-01-04 09:00+05:30'),
('Dev',    'Malhotra', 'dev.malhotra@example.com',  '9820054321', 'Jaipur',    'India',      100, TRUE,  '2026-01-20 18:00+05:30');

-- CATEGORIES (8): parents first, then children --------------------------
INSERT INTO categories (name, parent_id) VALUES
('Electronics',    NULL),   -- 1
('Clothing',       NULL),   -- 2
('Home & Kitchen', NULL),   -- 3
('Books',          NULL),   -- 4
('Sports',         NULL),   -- 5
('Smartphones',    1),      -- 6
('Laptops',        1),      -- 7
('Headphones',     1);      -- 8

-- PRODUCTS (21) ---------------------------------------------------------
INSERT INTO products (sku, name, brand, category_id, price, cost, stock_qty, is_available) VALUES
('PH-001', 'Samsung Galaxy S24',          'Samsung',   6, 79999.00, 62000.00,  25, TRUE),   -- 1
('PH-002', 'OnePlus 12',                  'OnePlus',   6, 64999.00, 51000.00,  40, TRUE),   -- 2
('LT-001', 'Dell Inspiron 15',            'Dell',      7, 55999.00, 44000.00,  15, TRUE),   -- 3
('LT-002', 'HP Pavilion 14',              'HP',        7, 62999.00, 50000.00,  12, TRUE),   -- 4
('LT-003', 'Lenovo IdeaPad Slim 3',       'Lenovo',    7, 42999.00, 34000.00,  30, TRUE),   -- 5
('HP-001', 'Sony WH-1000XM5',             'Sony',      8, 29990.00, 21000.00,  18, TRUE),   -- 6
('HP-002', 'boAt Rockerz 450',            'boAt',      8,  1499.00,   800.00, 200, TRUE),   -- 7
('HP-003', 'JBL Tune 760NC',              'JBL',       8,  5999.00,  3800.00,  60, TRUE),   -- 8
('CL-001', 'Levi''s 511 Slim Jeans',      'Levi''s',   2,  3499.00,  1900.00,  90, TRUE),   -- 9
('CL-002', 'Allen Solly Formal Shirt',    'Allen Solly',2, 1799.00,   900.00, 120, TRUE),   -- 10
('CL-003', 'Nike Running T-Shirt',        'Nike',      2,  1299.00,   650.00, 150, TRUE),   -- 11
('HK-001', 'Prestige Induction Cooktop',  'Prestige',  3,  2799.00,  1800.00,  45, TRUE),   -- 12
('HK-002', 'Philips Air Fryer',           'Philips',   3,  7999.00,  5200.00,  35, TRUE),   -- 13
('HK-003', 'Milton Steel Bottle',         'Milton',    3,   599.00,   250.00, 300, TRUE),   -- 14
('BK-001', 'Atomic Habits',               'Penguin',   4,   499.00,   250.00, 180, TRUE),   -- 15
('BK-002', 'The Alchemist',               'HarperCollins',4, 299.00,  140.00, 220, TRUE),   -- 16
('BK-003', 'Clean Code',                  'Pearson',   4,  3200.00,  2000.00,  40, TRUE),   -- 17
('SP-001', 'Yoga Mat',                    'Decathlon', 5,   799.00,   350.00, 100, TRUE),   -- 18
('SP-002', 'Cosco Football',              'Cosco',     5,   899.00,   450.00,   0, FALSE),  -- 19 (out of stock)
('SP-003', 'Yonex Badminton Racket',      'Yonex',     5,  2499.00,  1500.00,  55, TRUE),   -- 20
('EL-001', 'Logitech Wireless Mouse',     'Logitech',  1,   899.00,   500.00,  75, TRUE);   -- 21 (never ordered)

-- ORDERS (20) -----------------------------------------------------------
INSERT INTO orders (customer_id, order_date, status, payment_method, shipping_city, shipping_country) VALUES
( 1, '2026-01-05 10:15', 'delivered',  'UPI',         'Mumbai',    'India'),     -- 1
( 2, '2026-01-12 14:30', 'delivered',  'Credit Card', 'Ahmedabad', 'India'),     -- 2
( 3, '2026-02-03 09:45', 'delivered',  'COD',         'Pune',      'India'),     -- 3
( 1, '2026-02-14 20:10', 'delivered',  'Credit Card', 'Mumbai',    'India'),     -- 4
( 4, '2026-02-20 11:00', 'cancelled',  'UPI',         'Chennai',   'India'),     -- 5
( 5, '2026-03-02 16:25', 'delivered',  'Debit Card',  'Delhi',     'India'),     -- 6
( 6, '2026-03-15 13:40', 'shipped',    'UPI',         'Hyderabad', 'India'),     -- 7
( 7, '2026-03-28 18:05', 'delivered',  'Net Banking', 'Kochi',     'India'),     -- 8
( 8, '2026-04-04 12:50', 'delivered',  'UPI',         'Bengaluru', 'India'),     -- 9
(10, '2026-04-18 15:15', 'delivered',  'Credit Card', 'Mumbai',    'India'),     -- 10
(11, '2026-05-01 10:00', 'delivered',  'PayPal',      'London',    'UK'),        -- 11
(12, '2026-05-09 21:30', 'returned',   'Credit Card', 'New York',  'USA'),       -- 12
( 2, '2026-06-10 17:20', 'delivered',  'UPI',         'Ahmedabad', 'India'),     -- 13
(13, '2026-06-22 08:55', 'shipped',    'Credit Card', 'Singapore', 'Singapore'), -- 14
( 5, '2026-07-07 19:45', 'pending',    'UPI',         'Delhi',     'India'),     -- 15
( 1, '2026-08-01 11:35', 'shipped',    'Credit Card', 'Mumbai',    'India'),     -- 16
(15, '2026-08-19 14:00', 'pending',    'COD',         'Jaipur',    'India'),     -- 17
( 8, '2026-09-05 10:20', 'delivered',  'UPI',         'Bengaluru', 'India'),     -- 18
(10, '2026-09-25 16:10', 'processing', 'Debit Card',  'Mumbai',    'India'),     -- 19
( 3, '2026-10-10 12:00', 'processing', 'UPI',         'Pune',      'India');     -- 20

-- ORDER_ITEMS (order_id, product_id, quantity, unit_price) --------------
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
( 1,  1, 1, 79999.00), ( 1,  7, 2,  1499.00),
( 2, 15, 2,   499.00), ( 2, 16, 1,   299.00), ( 2, 14, 1,   599.00),
( 3,  9, 1,  3499.00), ( 3, 10, 2,  1799.00),
( 4,  6, 1, 29990.00),
( 5,  3, 1, 55999.00),
( 6, 13, 1,  7999.00), ( 6, 12, 1,  2799.00),
( 7,  2, 1, 64999.00),
( 8, 17, 1,  3200.00), ( 8, 15, 1,   499.00),
( 9, 20, 1,  2499.00), ( 9, 18, 2,   799.00),
(10,  4, 1, 62999.00), (10,  8, 1,  5999.00),
(11,  6, 1, 29990.00), (11, 11, 3,  1299.00),
(12,  5, 1, 42999.00),
(13,  8, 2,  5999.00), (13, 14, 3,   599.00),
(14,  1, 1, 79999.00),
(15,  9, 2,  3499.00),
(16, 13, 1,  7999.00), (16,  7, 1,  1499.00),
(17, 19, 2,   899.00), (17, 18, 1,   799.00),
(18, 17, 2,  3200.00), (18, 16, 2,   299.00),
(19, 10, 1,  1799.00), (19, 11, 1,  1299.00),
(20,  2, 1, 64999.00), (20,  8, 1,  5999.00);

-- Calculate order totals from line items (an UPDATE ... subquery workflow)
UPDATE orders o
SET total_amount = (SELECT SUM(oi.quantity * oi.unit_price)
                    FROM order_items oi
                    WHERE oi.order_id = o.order_id);

-- REVIEWS (15) ----------------------------------------------------------
INSERT INTO reviews (product_id, customer_id, rating, comment, created_at) VALUES
( 1,  1, 5, 'Excellent camera and display',        '2026-01-20 10:00'),
( 7,  1, 4, 'Good value for money',                '2026-01-21 10:00'),
( 6,  1, 5, 'Best noise cancellation I have used', '2026-03-01 09:00'),
(15,  2, 5, 'Life changing book',                  '2026-01-25 18:00'),
(16,  2, 4, 'Beautiful short read',                '2026-01-26 18:00'),
( 9,  3, 3, 'Fit is okay, colour faded a bit',     '2026-02-15 12:00'),
(10,  3, 4, 'Great for office wear',               '2026-02-16 12:00'),
(13,  5, 5, 'Cooks evenly and saves oil',          '2026-03-20 20:00'),
(12,  5, 4, 'Works well, a bit heavy',             '2026-03-21 20:00'),
(17,  7, 5, 'Must read for every developer',       '2026-04-05 09:30'),
(20,  8, 4, 'Light and well balanced',             '2026-04-15 17:00'),
(18,  8, 3, 'Slightly thin',                       '2026-04-16 17:00'),
( 4, 10, 4, 'Smooth performance for the price',    '2026-05-10 14:00'),
( 6, 11, 5, 'Worth every penny',                   '2026-05-20 08:00'),
( 5, 12, 2, 'Stopped working, had to return',      '2026-05-30 22:00'),
( 8,  2, 4, 'Solid sound, comfortable fit',        '2026-06-25 11:00'),
(11, 11, 3, NULL,                                  '2026-05-22 08:30');

-- Sanity check: row counts
SELECT 'customers' AS tbl, COUNT(*) FROM customers
UNION ALL SELECT 'categories',  COUNT(*) FROM categories
UNION ALL SELECT 'products',    COUNT(*) FROM products
UNION ALL SELECT 'orders',      COUNT(*) FROM orders
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL SELECT 'reviews',     COUNT(*) FROM reviews;
