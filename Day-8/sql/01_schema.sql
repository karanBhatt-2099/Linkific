DROP TABLE IF EXISTS reviews     CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders      CASCADE;
DROP TABLE IF EXISTS products    CASCADE;
DROP TABLE IF EXISTS categories  CASCADE;
DROP TABLE IF EXISTS customers   CASCADE;

-- ---------------------------------------------------------------------
-- CUSTOMERS
-- ---------------------------------------------------------------------
CREATE TABLE customers (
    customer_id    INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name     VARCHAR(50)  NOT NULL,
    last_name      VARCHAR(50)  NOT NULL,
    email          VARCHAR(120) NOT NULL UNIQUE,
    phone          VARCHAR(20),
    city           VARCHAR(60),
    country        VARCHAR(60)  NOT NULL DEFAULT 'India',
    loyalty_points INT          NOT NULL DEFAULT 0 CHECK (loyalty_points >= 0),
    is_active      BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------
-- CATEGORIES (self-referencing: a category can have a parent)
-- ---------------------------------------------------------------------
CREATE TABLE categories (
    category_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        VARCHAR(80) NOT NULL UNIQUE,
    parent_id   INT REFERENCES categories(category_id) ON DELETE SET NULL
);

-- ---------------------------------------------------------------------
-- PRODUCTS
-- ---------------------------------------------------------------------
CREATE TABLE products (
    product_id   INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sku          VARCHAR(20)   NOT NULL UNIQUE,
    name         VARCHAR(150)  NOT NULL,
    brand        VARCHAR(60),
    category_id  INT           NOT NULL REFERENCES categories(category_id),
    price        NUMERIC(10,2) NOT NULL CHECK (price > 0),
    cost         NUMERIC(10,2) NOT NULL CHECK (cost >= 0),
    stock_qty    INT           NOT NULL DEFAULT 0 CHECK (stock_qty >= 0),
    is_available BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_price_above_cost CHECK (price >= cost)
);

-- ---------------------------------------------------------------------
-- ORDERS
-- ---------------------------------------------------------------------
CREATE TABLE orders (
    order_id         INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id      INT           NOT NULL REFERENCES customers(customer_id),
    order_date       TIMESTAMP     NOT NULL DEFAULT NOW(),
    status           VARCHAR(20)   NOT NULL DEFAULT 'pending'
                     CHECK (status IN ('pending','processing','shipped','delivered','cancelled','returned')),
    payment_method   VARCHAR(30)   NOT NULL,
    shipping_city    VARCHAR(60),
    shipping_country VARCHAR(60)   NOT NULL DEFAULT 'India',
    total_amount     NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (total_amount >= 0)
);

-- ---------------------------------------------------------------------
-- ORDER_ITEMS (junction table: orders <-> products, many-to-many)
-- ---------------------------------------------------------------------
CREATE TABLE order_items (
    order_item_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id      INT           NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id    INT           NOT NULL REFERENCES products(product_id),
    quantity      INT           NOT NULL CHECK (quantity > 0),
    unit_price    NUMERIC(10,2) NOT NULL CHECK (unit_price > 0),
    CONSTRAINT uq_order_product UNIQUE (order_id, product_id)
);

-- ---------------------------------------------------------------------
-- REVIEWS
-- ---------------------------------------------------------------------
CREATE TABLE reviews (
    review_id   INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id  INT         NOT NULL REFERENCES products(product_id)  ON DELETE CASCADE,
    customer_id INT         NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    rating      SMALLINT    NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment     TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_one_review_per_customer UNIQUE (product_id, customer_id)
);

-- ---------------------------------------------------------------------
-- INDEXES (foreign keys are NOT indexed automatically in PostgreSQL)
-- ---------------------------------------------------------------------
CREATE INDEX idx_products_category    ON products(category_id);
CREATE INDEX idx_orders_customer      ON orders(customer_id);
CREATE INDEX idx_orders_order_date    ON orders(order_date);
CREATE INDEX idx_order_items_product  ON order_items(product_id);
CREATE INDEX idx_reviews_product      ON reviews(product_id);
CREATE INDEX idx_customers_city       ON customers(city);
CREATE INDEX idx_products_name_lower  ON products(LOWER(name));            -- expression index
CREATE INDEX idx_orders_open          ON orders(status)
       WHERE status IN ('pending','processing');                           -- partial index

-- Verify
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' ORDER BY table_name;
