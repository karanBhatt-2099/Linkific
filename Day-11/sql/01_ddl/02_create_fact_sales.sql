DROP TABLE IF EXISTS dw.fact_sales CASCADE;

CREATE TABLE dw.fact_sales (
    sales_key         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Foreign keys (point to SURROGATE keys of dimensions)
    date_key          INTEGER NOT NULL REFERENCES dw.dim_date(date_key),
    customer_key      INTEGER NOT NULL REFERENCES dw.dim_customer(customer_key),
    product_key       INTEGER NOT NULL REFERENCES dw.dim_product(product_key),
    store_key         INTEGER NOT NULL REFERENCES dw.dim_store(store_key),

    -- Degenerate dimensions (identify the grain, live in the fact table)
    order_id          VARCHAR(12) NOT NULL,
    order_line_number SMALLINT    NOT NULL,

    -- Measures
    quantity          INTEGER       NOT NULL CHECK (quantity > 0),
    unit_price        NUMERIC(12,2) NOT NULL,
    discount_amount   NUMERIC(12,2) NOT NULL DEFAULT 0,
    sales_amount      NUMERIC(12,2) NOT NULL,   -- quantity*unit_price - discount
    cost_amount       NUMERIC(12,2) NOT NULL,   -- quantity*unit_cost
    profit_amount     NUMERIC(12,2) NOT NULL,   -- sales_amount - cost_amount

    -- Enforce the grain: no duplicate order lines
    CONSTRAINT uq_fact_sales_grain UNIQUE (order_id, order_line_number)
);

-- Indexes on foreign keys make joins/filters faster.
CREATE INDEX idx_fact_sales_date     ON dw.fact_sales (date_key);
CREATE INDEX idx_fact_sales_customer ON dw.fact_sales (customer_key);
CREATE INDEX idx_fact_sales_product  ON dw.fact_sales (product_key);
CREATE INDEX idx_fact_sales_store    ON dw.fact_sales (store_key);

-- Validation: expect 13 columns
SELECT column_name, data_type
FROM   information_schema.columns
WHERE  table_schema = 'dw' AND table_name = 'fact_sales'
ORDER  BY ordinal_position;
