DROP TABLE IF EXISTS dw_snowflake.fact_sales      CASCADE;
DROP TABLE IF EXISTS dw_snowflake.dim_product     CASCADE;
DROP TABLE IF EXISTS dw_snowflake.dim_subcategory CASCADE;
DROP TABLE IF EXISTS dw_snowflake.dim_category    CASCADE;
DROP TABLE IF EXISTS dw_snowflake.dim_store       CASCADE;
DROP TABLE IF EXISTS dw_snowflake.dim_region      CASCADE;

CREATE TABLE dw_snowflake.dim_category (
    category_key  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE dw_snowflake.dim_subcategory (
    subcategory_key  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    subcategory_name VARCHAR(50) NOT NULL,
    category_key     INTEGER NOT NULL REFERENCES dw_snowflake.dim_category(category_key),
    UNIQUE (subcategory_name, category_key)
);

CREATE TABLE dw_snowflake.dim_product (
    product_key     INTEGER PRIMARY KEY,             -- same keys as star
    product_id      VARCHAR(10)  NOT NULL UNIQUE,
    product_name    VARCHAR(100) NOT NULL,
    brand           VARCHAR(50),
    unit_cost       NUMERIC(12,2) NOT NULL,
    unit_price      NUMERIC(12,2) NOT NULL,
    subcategory_key INTEGER NOT NULL REFERENCES dw_snowflake.dim_subcategory(subcategory_key)
);

CREATE TABLE dw_snowflake.dim_region (
    region_key  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    region_name VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE dw_snowflake.dim_store (
    store_key  INTEGER PRIMARY KEY,                  -- same keys as star
    store_id   VARCHAR(10)  NOT NULL UNIQUE,
    store_name VARCHAR(100) NOT NULL,
    city       VARCHAR(50),
    state      VARCHAR(50),
    store_type VARCHAR(20) NOT NULL,
    region_key INTEGER NOT NULL REFERENCES dw_snowflake.dim_region(region_key)
);

-- The snowflake fact keeps the same grain/measures; date & customer
-- dimensions are reused from the star schema (dw).
CREATE TABLE dw_snowflake.fact_sales (
    sales_key    BIGINT PRIMARY KEY,
    date_key     INTEGER NOT NULL REFERENCES dw.dim_date(date_key),
    customer_key INTEGER NOT NULL REFERENCES dw.dim_customer(customer_key),
    product_key  INTEGER NOT NULL REFERENCES dw_snowflake.dim_product(product_key),
    store_key    INTEGER NOT NULL REFERENCES dw_snowflake.dim_store(store_key),
    order_id     VARCHAR(12) NOT NULL,
    quantity     INTEGER NOT NULL,
    sales_amount NUMERIC(12,2) NOT NULL,
    profit_amount NUMERIC(12,2) NOT NULL
);
