-- Day 22: Snowflake setup for the E-commerce Analytics Platform
-- Run this once in a Snowflake worksheet.

USE ROLE ACCOUNTADMIN;

-- 1. Warehouse (compute) – smallest size, auto-suspends to save credits
CREATE WAREHOUSE IF NOT EXISTS ECOM_WH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND   = 60
    AUTO_RESUME    = TRUE;

-- 2. Database + schemas
CREATE DATABASE IF NOT EXISTS ECOM_DB;
CREATE SCHEMA IF NOT EXISTS ECOM_DB.RAW;         -- untouched copy of source data
CREATE SCHEMA IF NOT EXISTS ECOM_DB.ANALYTICS;   -- star schema for BI

USE WAREHOUSE ECOM_WH;

-- 3. RAW tables
CREATE TABLE IF NOT EXISTS ECOM_DB.RAW.PRODUCTS (
    id           INT,
    title        STRING,
    price        FLOAT,
    category     STRING,
    rating_rate  FLOAT,
    rating_count INT,
    loaded_at    TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS ECOM_DB.RAW.USERS (
    id         INT,
    email      STRING,
    first_name STRING,
    last_name  STRING,
    city       STRING,
    loaded_at  TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS ECOM_DB.RAW.CART_ITEMS (
    cart_id    INT,
    user_id    INT,
    cart_date  DATE,
    product_id INT,
    quantity   INT,
    loaded_at  TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- 4. ANALYTICS tables (star schema)
CREATE TABLE IF NOT EXISTS ECOM_DB.ANALYTICS.DIM_DATE (
    date_key    INT PRIMARY KEY,      -- e.g. 20261106
    full_date   DATE,
    year        INT,
    quarter     INT,
    month       INT,
    month_name  STRING,
    day_of_week STRING
);

CREATE TABLE IF NOT EXISTS ECOM_DB.ANALYTICS.DIM_PRODUCT (
    product_key INT PRIMARY KEY,
    title       STRING,
    category    STRING,
    price       FLOAT,
    rating      FLOAT
);

CREATE TABLE IF NOT EXISTS ECOM_DB.ANALYTICS.DIM_CUSTOMER (
    customer_key INT PRIMARY KEY,
    full_name    STRING,
    email        STRING,
    city         STRING
);

CREATE TABLE IF NOT EXISTS ECOM_DB.ANALYTICS.FACT_SALES (
    cart_id      INT,
    date_key     INT,
    customer_key INT,
    product_key  INT,
    quantity     INT,
    unit_price   FLOAT,
    total_amount FLOAT
);
