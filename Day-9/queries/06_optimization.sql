
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);


CREATE INDEX IF NOT EXISTS idx_orders_cust_status_date ON orders(customer_id, status, order_date);


CREATE INDEX IF NOT EXISTS idx_items_order_cover ON order_items(order_id, quantity);


CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);

