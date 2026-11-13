-- 01: Warehouse schema (Snowflake: PK/FK are informational, not enforced; no indexes -> clustering keys)
CREATE DATABASE IF NOT EXISTS {{DB}};
USE DATABASE {{DB}};
CREATE SCHEMA IF NOT EXISTS STG;
CREATE SCHEMA IF NOT EXISTS DW;
USE SCHEMA DW;

CREATE TABLE IF NOT EXISTS dim_date (
  date_key        NUMBER(8)    NOT NULL,
  full_date       DATE         NOT NULL,
  day_of_month    NUMBER(2),
  day_of_week     NUMBER(1),            -- 1=Mon..7=Sun (ISO)
  day_name        VARCHAR(10),
  day_of_year     NUMBER(3),
  week_of_year    NUMBER(2),
  month_num       NUMBER(2),
  month_name      VARCHAR(10),
  year_month      VARCHAR(7),
  quarter_num     NUMBER(1),
  quarter_name    VARCHAR(2),
  year_num        NUMBER(4),
  fiscal_year     NUMBER(4),            -- fiscal year starts 1 April
  fiscal_quarter  NUMBER(1),
  month_start_date DATE,
  month_end_date  DATE,
  is_weekend      BOOLEAN,
  is_holiday      BOOLEAN DEFAULT FALSE,
  holiday_name    VARCHAR(60),
  CONSTRAINT pk_dim_date PRIMARY KEY (date_key) RELY,
  CONSTRAINT uq_dim_date UNIQUE (full_date)
);

CREATE TABLE IF NOT EXISTS dim_customer (          -- SCD Type 2
  customer_key   NUMBER AUTOINCREMENT START 1 INCREMENT 1,
  customer_id    VARCHAR(20)  NOT NULL,            -- business key
  customer_name  VARCHAR(100),
  email          VARCHAR(150),
  city           VARCHAR(60),                      -- tracked
  segment        VARCHAR(30),                      -- tracked
  signup_date    DATE,
  effective_date DATE         NOT NULL,
  end_date       DATE         NOT NULL,            -- exclusive; 9999-12-31 = open
  is_current     BOOLEAN      NOT NULL,
  row_hash       VARCHAR(32),
  CONSTRAINT pk_dim_customer PRIMARY KEY (customer_key) RELY
);

CREATE TABLE IF NOT EXISTS dim_product (           -- SCD Type 1
  product_key   NUMBER AUTOINCREMENT START 1 INCREMENT 1,
  product_id    VARCHAR(20) NOT NULL,
  product_name  VARCHAR(100),
  category      VARCHAR(40),
  brand         VARCHAR(40),
  unit_cost     NUMBER(12,2),
  list_price    NUMBER(12,2),
  CONSTRAINT pk_dim_product PRIMARY KEY (product_key) RELY,
  CONSTRAINT uq_dim_product UNIQUE (product_id)
);

CREATE TABLE IF NOT EXISTS dim_store (             -- SCD Type 1
  store_key   NUMBER AUTOINCREMENT START 1 INCREMENT 1,
  store_id    VARCHAR(20) NOT NULL,
  store_name  VARCHAR(80),
  city        VARCHAR(60),
  region      VARCHAR(30),
  open_date   DATE,
  CONSTRAINT pk_dim_store PRIMARY KEY (store_key) RELY,
  CONSTRAINT uq_dim_store UNIQUE (store_id)
);

CREATE TABLE IF NOT EXISTS fact_sales (
  sales_key       NUMBER AUTOINCREMENT START 1 INCREMENT 1,
  sale_id         VARCHAR(20) NOT NULL,            -- degenerate/source key
  order_id        VARCHAR(20) NOT NULL,
  date_key        NUMBER(8)   NOT NULL,
  customer_key    NUMBER      NOT NULL,
  product_key     NUMBER      NOT NULL,
  store_key       NUMBER      NOT NULL,
  quantity        NUMBER(10,0),
  unit_price      NUMBER(12,2),
  discount_pct    NUMBER(5,2),
  gross_amount    NUMBER(14,2),
  discount_amount NUMBER(14,2),
  net_amount      NUMBER(14,2),
  cost_amount     NUMBER(14,2),
  profit_amount   NUMBER(14,2),
  load_ts         TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
  CONSTRAINT pk_fact_sales PRIMARY KEY (sales_key) RELY,
  CONSTRAINT uq_fact_sale_id UNIQUE (sale_id),
  CONSTRAINT fk_fs_date     FOREIGN KEY (date_key)     REFERENCES dim_date(date_key)         RELY,
  CONSTRAINT fk_fs_customer FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key) RELY,
  CONSTRAINT fk_fs_product  FOREIGN KEY (product_key)  REFERENCES dim_product(product_key)   RELY,
  CONSTRAINT fk_fs_store    FOREIGN KEY (store_key)    REFERENCES dim_store(store_key)       RELY
);

ALTER TABLE fact_sales CLUSTER BY (date_key);      -- Snowflake's "index" for large tables

CREATE TABLE IF NOT EXISTS validation_results (
  run_id VARCHAR, run_ts TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
  category VARCHAR, check_name VARCHAR, expected NUMBER, actual NUMBER, status VARCHAR
);
