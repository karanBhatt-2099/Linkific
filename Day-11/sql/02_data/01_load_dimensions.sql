TRUNCATE dw.fact_inventory, dw.fact_sales,
         dw.dim_store, dw.dim_product, dw.dim_customer, dw.dim_date
RESTART IDENTITY CASCADE;

-- ---------------------------------------------------------------------
-- 1) DATE DIMENSION: one row per day for 2025 and 2026 (730 rows).
--    generate_series creates the dates; the other columns are derived.
-- ---------------------------------------------------------------------
INSERT INTO dw.dim_date
SELECT
    TO_CHAR(d, 'YYYYMMDD')::INT          AS date_key,
    d::DATE                              AS full_date,
    EXTRACT(DAY     FROM d)::SMALLINT    AS day_of_month,
    EXTRACT(ISODOW  FROM d)::SMALLINT    AS day_of_week,
    TRIM(TO_CHAR(d, 'Day'))              AS day_name,
    EXTRACT(WEEK    FROM d)::SMALLINT    AS week_of_year,
    EXTRACT(MONTH   FROM d)::SMALLINT    AS month_number,
    TRIM(TO_CHAR(d, 'Month'))            AS month_name,
    EXTRACT(QUARTER FROM d)::SMALLINT    AS quarter,
    EXTRACT(YEAR    FROM d)::SMALLINT    AS year,
    EXTRACT(ISODOW  FROM d) IN (6, 7)    AS is_weekend
FROM generate_series(DATE '2025-01-01', DATE '2026-12-31', INTERVAL '1 day') AS d;

-- ---------------------------------------------------------------------
-- 2) CUSTOMER DIMENSION (10 customers, all current versions)
--    customer_key is generated automatically (1..10).
-- ---------------------------------------------------------------------
INSERT INTO dw.dim_customer (customer_id, full_name, email, city, state, segment) VALUES
('C001', 'Aarav Sharma', 'aarav.sharma@example.com', 'Mumbai',    'Maharashtra',  'Consumer'),
('C002', 'Priya Patel',  'priya.patel@example.com',  'Ahmedabad', 'Gujarat',      'Corporate'),
('C003', 'Rahul Verma',  'rahul.verma@example.com',  'Delhi',     'Delhi',        'Consumer'),
('C004', 'Sneha Iyer',   'sneha.iyer@example.com',   'Chennai',   'Tamil Nadu',   'Home Office'),
('C005', 'Vikram Singh', 'vikram.singh@example.com', 'Jaipur',    'Rajasthan',    'Corporate'),
('C006', 'Ananya Das',   'ananya.das@example.com',   'Kolkata',   'West Bengal',  'Consumer'),
('C007', 'Rohan Mehta',  'rohan.mehta@example.com',  'Pune',      'Maharashtra',  'Consumer'),
('C008', 'Kavya Nair',   'kavya.nair@example.com',   'Kochi',     'Kerala',       'Home Office'),
('C009', 'Arjun Reddy',  'arjun.reddy@example.com',  'Hyderabad', 'Telangana',    'Corporate'),
('C010', 'Meera Joshi',  'meera.joshi@example.com',  'Bengaluru', 'Karnataka',    'Consumer');

-- ---------------------------------------------------------------------
-- 3) PRODUCT DIMENSION (12 products, prices in INR)
-- ---------------------------------------------------------------------
INSERT INTO dw.dim_product (product_id, product_name, category, subcategory, brand, unit_cost, unit_price) VALUES
('P001', 'Laptop Pro 14',                 'Electronics', 'Computers',   'TechNova',  55000, 70000),
('P002', 'Wireless Mouse',                'Electronics', 'Accessories', 'TechNova',    400,   800),
('P003', 'Mechanical Keyboard',           'Electronics', 'Accessories', 'KeyCraft',   2000,  3500),
('P004', 'Smartphone X',                  'Electronics', 'Phones',      'Zenith',    20000, 28000),
('P005', 'Noise Cancelling Headphones',   'Electronics', 'Audio',       'SoundWave',  4000,  7000),
('P006', 'Ergonomic Office Chair',        'Furniture',   'Chairs',      'ComfortCo',  5000,  9000),
('P007', 'Standing Desk',                 'Furniture',   'Desks',       'ComfortCo', 12000, 18000),
('P008', 'Bookshelf',                     'Furniture',   'Storage',     'HomeBase',   3000,  5500),
('P009', 'Notebook Pack (5)',             'Stationery',  'Paper',       'PaperPlus',   150,   300),
('P010', 'Gel Pen Box (10)',              'Stationery',  'Writing',     'PaperPlus',    60,   150),
('P011', 'LED Desk Lamp',                 'Furniture',   'Lighting',    'HomeBase',    700,  1500),
('P012', 'Tablet Mini',                   'Electronics', 'Computers',   'Zenith',    15000, 22000);

-- ---------------------------------------------------------------------
-- 4) STORE DIMENSION (3 physical stores + 1 online)
-- ---------------------------------------------------------------------
INSERT INTO dw.dim_store (store_id, store_name, city, state, region, store_type) VALUES
('S01', 'Mumbai Flagship',      'Mumbai',    'Maharashtra', 'West',   'Flagship'),
('S02', 'Delhi Central',        'Delhi',     'Delhi',       'North',  'Retail'),
('S03', 'Bengaluru Tech Park',  'Bengaluru', 'Karnataka',   'South',  'Retail'),
('S04', 'Online Store',         'Online',    'Online',      'Online', 'Online');

-- Validation: expect 730 | 10 | 12 | 4
SELECT (SELECT COUNT(*) FROM dw.dim_date)     AS dates,
       (SELECT COUNT(*) FROM dw.dim_customer) AS customers,
       (SELECT COUNT(*) FROM dw.dim_product)  AS products,
       (SELECT COUNT(*) FROM dw.dim_store)    AS stores;
