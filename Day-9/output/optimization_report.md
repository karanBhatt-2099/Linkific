# Query Optimization Report

Benchmark DB: **30,500 orders**, **76,270 order_items**. Timings are best-of-3 in milliseconds (SQLite, your machine will differ; the *ratios* matter).

## OPT1 Index on filter column

**Why:** Without an index the engine scans every row. A B-tree index turns it into a direct lookup.

**Before** (0.96 ms)
```sql
SELECT COUNT(*) FROM orders WHERE customer_id = 42
```
Plan: `SCAN orders`

**After** (0.02 ms, **47.7x faster**)
```sql
SELECT COUNT(*) FROM orders WHERE customer_id = 42
```
Plan: `SEARCH orders USING COVERING INDEX idx_orders_customer (customer_id=?)`

Results identical: **True**

## OPT2 Composite index (filter + sort)

**Why:** Equality columns first, then the sort column: the index returns rows already ordered, so no sort step.

**Before** (1.50 ms)
```sql
SELECT order_id, order_date FROM orders WHERE customer_id=42 AND status='completed' ORDER BY order_date
```
Plan: `SCAN orders | USE TEMP B-TREE FOR ORDER BY`

**After** (0.22 ms, **6.8x faster**)
```sql
SELECT order_id, order_date FROM orders WHERE customer_id=42 AND status='completed' ORDER BY order_date
```
Plan: `SEARCH orders USING COVERING INDEX idx_orders_cust_status_date (customer_id=? AND status=?)`

Results identical: **True**

## OPT3 Covering index

**Why:** When the index contains every column the query needs, the table itself is never touched.

**Before** (29.52 ms)
```sql
SELECT order_id, SUM(quantity) FROM order_items GROUP BY order_id
```
Plan: `SCAN order_items | USE TEMP B-TREE FOR GROUP BY`

**After** (21.21 ms, **1.4x faster**)
```sql
SELECT order_id, SUM(quantity) FROM order_items GROUP BY order_id
```
Plan: `SCAN order_items USING COVERING INDEX idx_items_order_cover`

Results identical: **True**

## OPT4 SARGable date filter

**Why:** Wrapping the column in strftime() hides it from the index. Compare the raw column to a range instead.

**Before** (5.99 ms)
```sql
SELECT COUNT(*) FROM orders WHERE strftime('%Y', order_date) = '2025'
```
Plan: `SCAN orders USING COVERING INDEX idx_orders_cust_status_date`

**After** (0.41 ms, **14.5x faster**)
```sql
SELECT COUNT(*) FROM orders WHERE order_date >= '2025-01-01' AND order_date < '2026-01-01'
```
Plan: `SEARCH orders USING COVERING INDEX idx_orders_date (order_date>? AND order_date<?)`

Results identical: **True**

## OPT5 Correlated subquery vs window function (trade-off)

**Why:** A correlated MAX() re-runs per outer row. Without a supporting index that is O(n^2) and the window function wins by a wide margin; BUT with an index on (customer_id, order_date) SQLite turns each MAX() into a single index seek, which can beat the window function's full sort. Lesson: measure, and check the plan. This benchmark deliberately gives the correlated query its index, so the window version is slower here.

**Before** (17.80 ms)
```sql
SELECT o.customer_id, o.order_id FROM orders o
       WHERE o.order_date = (SELECT MAX(o2.order_date) FROM orders o2 WHERE o2.customer_id = o.customer_id)
```
Plan: `SCAN o USING COVERING INDEX idx_orders_cust_date | CORRELATED SCALAR SUBQUERY 1 | SEARCH o2 USING COVERING INDEX idx_orders_cust_date (customer_id=?)`

**After** (32.89 ms, **0.5x faster**)
```sql
SELECT customer_id, order_id FROM (
         SELECT customer_id, order_id,
                RANK() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS rk
         FROM orders) WHERE rk = 1
```
Plan: `CO-ROUTINE (subquery-1) | CO-ROUTINE (subquery-3) | SCAN orders USING COVERING INDEX idx_orders_cust_date | USE TEMP B-TREE FOR RIGHT PART OF ORDER BY | SCAN (subquery-3) | SCAN (subquery-1)`

Results identical: **True**

## OPT6 Aggregate before joining (avoid fan-out)

**Why:** Pre-aggregating order_items to one row per order shrinks the join input before the expensive grouping.

**Before** (28.42 ms)
```sql
SELECT o.customer_id, SUM(oi.quantity*oi.unit_price) AS spend
       FROM orders o JOIN order_items oi ON oi.order_id=o.order_id
       WHERE o.status='completed' GROUP BY o.customer_id
```
Plan: `SCAN oi | SEARCH o USING INTEGER PRIMARY KEY (rowid=?) | USE TEMP B-TREE FOR GROUP BY`

**After** (21.45 ms, **1.3x faster**)
```sql
WITH per_order AS (SELECT order_id, SUM(quantity*unit_price) AS v FROM order_items GROUP BY order_id)
       SELECT o.customer_id, SUM(po.v) AS spend
       FROM orders o JOIN per_order po ON po.order_id=o.order_id
       WHERE o.status='completed' GROUP BY o.customer_id
```
Plan: `CO-ROUTINE per_order | SCAN order_items USING COVERING INDEX idx_items_order_cover | SCAN po | SEARCH o USING INTEGER PRIMARY KEY (rowid=?) | USE TEMP B-TREE FOR GROUP BY`

Results identical: **True**

## OPT7 UNION -> UNION ALL

**Why:** UNION must sort/deduplicate the combined result. UNION ALL just appends (use when overlap is impossible or fine).

**Before** (4.39 ms)
```sql
SELECT order_id FROM orders WHERE status='cancelled' UNION SELECT order_id FROM orders WHERE status='returned'
```
Plan: `COMPOUND QUERY | LEFT-MOST SUBQUERY | SCAN orders | UNION USING TEMP B-TREE | SCAN orders`

**After** (3.66 ms, **1.2x faster**)
```sql
SELECT order_id FROM orders WHERE status='cancelled' UNION ALL SELECT order_id FROM orders WHERE status='returned'
```
Plan: `COMPOUND QUERY | LEFT-MOST SUBQUERY | SCAN orders | UNION ALL | SCAN orders`

Results identical: **True**

## OPT8 OFFSET -> keyset pagination

**Why:** OFFSET reads and throws away every skipped row. Keyset seeks straight to the next page by key.

**Before** (0.27 ms)
```sql
SELECT order_id, order_date FROM orders ORDER BY order_id LIMIT 20 OFFSET 30000
```
Plan: `SCAN orders`

**After** (0.01 ms, **20.1x faster**)
```sql
SELECT order_id, order_date FROM orders WHERE order_id > 39500 ORDER BY order_id LIMIT 20
```
Plan: `SEARCH orders USING INTEGER PRIMARY KEY (rowid>?)`

Results identical: **True**

## OPT9 IN (subquery) -> EXISTS

**Why:** EXISTS can stop at the first match per customer; combined with an index it avoids materializing the list.

**Before** (1.44 ms)
```sql
SELECT c.customer_id FROM customers c WHERE c.customer_id IN (SELECT customer_id FROM orders WHERE status='returned')
```
Plan: `SEARCH c USING INTEGER PRIMARY KEY (rowid=?) | LIST SUBQUERY 1 | SCAN orders`

**After** (0.04 ms, **34.0x faster**)
```sql
SELECT c.customer_id FROM customers c WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id=c.customer_id AND o.status='returned')
```
Plan: `SCAN c | CORRELATED SCALAR SUBQUERY 1 | SEARCH o USING COVERING INDEX idx_orders_cust_status (customer_id=? AND status=?)`

Results identical: **True**

## OPT10 Filter early with WHERE, not HAVING

**Why:** WHERE removes rows before grouping; HAVING on a non-aggregate makes the engine group everything first.

**Before** (2.02 ms)
```sql
SELECT status, COUNT(*) c FROM orders GROUP BY status HAVING status = 'completed'
```
Plan: `SCAN orders USING COVERING INDEX idx_orders_cust_status`

**After** (1.71 ms, **1.2x faster**)
```sql
SELECT status, COUNT(*) c FROM orders WHERE status = 'completed' GROUP BY status
```
Plan: `SEARCH orders USING COVERING INDEX idx_orders_status (status=?)`

Results identical: **True**

## Summary

| Experiment | Before (ms) | After (ms) | Speed-up | Same result |
|---|---:|---:|---:|:--:|
| OPT1 Index on filter column | 0.96 | 0.02 | 47.7x | yes |
| OPT2 Composite index (filter + sort) | 1.50 | 0.22 | 6.8x | yes |
| OPT3 Covering index | 29.52 | 21.21 | 1.4x | yes |
| OPT4 SARGable date filter | 5.99 | 0.41 | 14.5x | yes |
| OPT5 Correlated subquery vs window function (trade-off) | 17.80 | 32.89 | 0.5x | yes |
| OPT6 Aggregate before joining (avoid fan-out) | 28.42 | 21.45 | 1.3x | yes |
| OPT7 UNION -> UNION ALL | 4.39 | 3.66 | 1.2x | yes |
| OPT8 OFFSET -> keyset pagination | 0.27 | 0.01 | 20.1x | yes |
| OPT9 IN (subquery) -> EXISTS | 1.44 | 0.04 | 34.0x | yes |
| OPT10 Filter early with WHERE, not HAVING | 2.02 | 1.71 | 1.2x | yes |
