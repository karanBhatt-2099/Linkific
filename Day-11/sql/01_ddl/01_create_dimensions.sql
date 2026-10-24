-- Drop in reverse dependency order so the script can be re-run safely.
DROP TABLE IF EXISTS dw.fact_inventory CASCADE;
DROP TABLE IF EXISTS dw.fact_sales     CASCADE;
DROP TABLE IF EXISTS dw.dim_store      CASCADE;
DROP TABLE IF EXISTS dw.dim_product    CASCADE;
DROP TABLE IF EXISTS dw.dim_customer   CASCADE;
DROP TABLE IF EXISTS dw.dim_date       CASCADE;

-- ---------------------------------------------------------------------
-- DATE DIMENSION  (WHEN)
-- The surrogate key is a smart integer YYYYMMDD (e.g. 20260315).
-- This is the one common exception where the key is human-readable.
-- ---------------------------------------------------------------------
CREATE TABLE dw.dim_date (
    date_key      INTEGER      PRIMARY KEY,          -- 20260315
    full_date     DATE         NOT NULL UNIQUE,
    day_of_month  SMALLINT     NOT NULL,
    day_of_week   SMALLINT     NOT NULL,             -- 1=Mon ... 7=Sun
    day_name      VARCHAR(10)  NOT NULL,
    week_of_year  SMALLINT     NOT NULL,
    month_number  SMALLINT     NOT NULL,
    month_name    VARCHAR(10)  NOT NULL,
    quarter       SMALLINT     NOT NULL,
    year          SMALLINT     NOT NULL,
    is_weekend    BOOLEAN      NOT NULL
);

-- ---------------------------------------------------------------------
-- CUSTOMER DIMENSION  (WHO)  - built as SCD Type 2 ready
-- customer_key = surrogate key (one per VERSION of a customer)
-- customer_id  = natural key   (same for every version)
-- effective_date / end_date / is_current track history.
-- ---------------------------------------------------------------------
CREATE TABLE dw.dim_customer (
    customer_key   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id    VARCHAR(10)  NOT NULL,            -- natural key
    full_name      VARCHAR(100) NOT NULL,
    email          VARCHAR(100),
    city           VARCHAR(50),
    state          VARCHAR(50),
    country        VARCHAR(50)  NOT NULL DEFAULT 'India',
    segment        VARCHAR(20),                      -- Consumer/Corporate/Home Office
    effective_date DATE         NOT NULL DEFAULT DATE '2025-01-01',
    end_date       DATE         NOT NULL DEFAULT DATE '9999-12-31',
    is_current     BOOLEAN      NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_dim_customer_version UNIQUE (customer_id, effective_date)
);

-- ---------------------------------------------------------------------
-- PRODUCT DIMENSION  (WHAT)
-- Category / subcategory are stored flat (denormalized) = STAR design.
-- ---------------------------------------------------------------------
CREATE TABLE dw.dim_product (
    product_key   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id    VARCHAR(10)   NOT NULL UNIQUE,     -- natural key
    product_name  VARCHAR(100)  NOT NULL,
    category      VARCHAR(50)   NOT NULL,
    subcategory   VARCHAR(50)   NOT NULL,
    brand         VARCHAR(50),
    unit_cost     NUMERIC(12,2) NOT NULL CHECK (unit_cost  >= 0),
    unit_price    NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0)
);

-- ---------------------------------------------------------------------
-- STORE DIMENSION  (WHERE)
-- ---------------------------------------------------------------------
CREATE TABLE dw.dim_store (
    store_key   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    store_id    VARCHAR(10)  NOT NULL UNIQUE,        -- natural key
    store_name  VARCHAR(100) NOT NULL,
    city        VARCHAR(50),
    state       VARCHAR(50),
    region      VARCHAR(20)  NOT NULL,               -- North/South/East/West/Online
    store_type  VARCHAR(20)  NOT NULL                -- Flagship/Retail/Online
);

-- Validation: expect 4 tables
SELECT table_name
FROM   information_schema.tables
WHERE  table_schema = 'dw'
ORDER  BY table_name;
