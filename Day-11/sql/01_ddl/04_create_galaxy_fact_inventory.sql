DROP TABLE IF EXISTS dw.fact_inventory CASCADE;

CREATE TABLE dw.fact_inventory (
    inventory_key    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    date_key         INTEGER NOT NULL REFERENCES dw.dim_date(date_key),
    product_key      INTEGER NOT NULL REFERENCES dw.dim_product(product_key),
    store_key        INTEGER NOT NULL REFERENCES dw.dim_store(store_key),
    quantity_on_hand INTEGER NOT NULL CHECK (quantity_on_hand >= 0),  -- semi-additive measure
    reorder_level    INTEGER NOT NULL,
    CONSTRAINT uq_fact_inventory_grain UNIQUE (date_key, product_key, store_key)
);

CREATE INDEX idx_fact_inv_date    ON dw.fact_inventory (date_key);
CREATE INDEX idx_fact_inv_product ON dw.fact_inventory (product_key);
CREATE INDEX idx_fact_inv_store   ON dw.fact_inventory (store_key);
