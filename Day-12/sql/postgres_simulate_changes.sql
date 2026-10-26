-- Run in pgAdmin AFTER the first pipeline run, then run `python main.py` again.
-- Only these 3 orders should be picked up (incremental load).
UPDATE orders SET status = 'shipped', updated_at = NOW() WHERE order_id = 1005;

INSERT INTO orders (order_id, customer_id, order_date, status, updated_at) VALUES
(1013, 2, '2026-10-25', 'pending',   NOW()),
(1014, 4, '2026-10-26', 'completed', NOW());
