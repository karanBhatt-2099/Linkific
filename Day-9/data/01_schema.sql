-- Day 9 dataset: a small e-commerce company
PRAGMA foreign_keys = ON;

CREATE TABLE regions (
    region_id   INTEGER PRIMARY KEY,
    region_name TEXT NOT NULL
);

CREATE TABLE employees (            -- self-join / recursive CTE target
    employee_id INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    title       TEXT NOT NULL,
    manager_id  INTEGER REFERENCES employees(employee_id),
    region_id   INTEGER REFERENCES regions(region_id),
    salary      INTEGER NOT NULL
);

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    email       TEXT NOT NULL,
    region_id   INTEGER REFERENCES regions(region_id),
    signup_date DATE NOT NULL,
    referred_by INTEGER REFERENCES customers(customer_id)
);

CREATE TABLE categories (           -- hierarchy for recursive CTE
    category_id INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    parent_id   INTEGER REFERENCES categories(category_id)
);

CREATE TABLE products (
    product_id  INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    category_id INTEGER REFERENCES categories(category_id),
    unit_price  REAL NOT NULL,
    unit_cost   REAL NOT NULL
);

CREATE TABLE orders (
    order_id    INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    employee_id INTEGER REFERENCES employees(employee_id),  -- sales rep
    order_date  DATE NOT NULL,
    status      TEXT NOT NULL CHECK (status IN ('completed','cancelled','returned'))
);

CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id      INTEGER NOT NULL REFERENCES orders(order_id),
    product_id    INTEGER NOT NULL REFERENCES products(product_id),
    quantity      INTEGER NOT NULL,
    unit_price    REAL NOT NULL,
    discount      REAL NOT NULL DEFAULT 0
);

-- Some products never sell and some customers never order, on purpose (for outer joins).
