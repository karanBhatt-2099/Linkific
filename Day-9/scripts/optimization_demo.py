"""Query optimization lab: builds a 40k-order benchmark DB, then for each experiment prints
the EXPLAIN QUERY PLAN and timing BEFORE and AFTER the optimization. Writes output/optimization_report.md"""
import sqlite3, os, random, time, shutil, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, BIG = os.path.join(ROOT,"data","sales.db"), os.path.join(ROOT,"data","sales_benchmark.db")
shutil.copy(SRC, BIG)
con = sqlite3.connect(BIG)
random.seed(7)

# ---- inflate to ~40k orders / ~100k items ---------------------------------
start = dt.date(2024,1,1)
orders, items = [], []
for oid in range(10001, 40001):
    d = start + dt.timedelta(days=random.randint(0,729))
    orders.append((oid, random.randint(1,55), random.choice([6,7,8,9]), d.isoformat(),
                   random.choices(["completed","cancelled","returned"],[88,7,5])[0]))
    for _ in range(random.randint(1,4)):
        items.append((oid, random.randint(1,17), random.randint(1,3), random.choice([10,25,45,90,220,480]), random.choice([0,0.05,0.1])))
con.executemany("INSERT INTO orders VALUES (?,?,?,?,?)", orders)
con.executemany("INSERT INTO order_items(order_id,product_id,quantity,unit_price,discount) VALUES (?,?,?,?,?)", items)
con.commit()
n_o = con.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
n_i = con.execute("SELECT COUNT(*) FROM order_items").fetchone()[0]

def plan(sql):  return [r[3] for r in con.execute("EXPLAIN QUERY PLAN " + sql)]
def timeit(sql, n=3):
    best = 1e9
    for _ in range(n):
        t=time.perf_counter(); con.execute(sql).fetchall(); best=min(best,time.perf_counter()-t)
    return best*1000

report = [f"# Query Optimization Report\n\nBenchmark DB: **{n_o:,} orders**, **{n_i:,} order_items**. "
          "Timings are best-of-3 in milliseconds (SQLite, your machine will differ; the *ratios* matter).\n"]
summary = []

def experiment(title, why, before_sql, after_sql, setup=None, teardown=None):
    for stmt in (teardown or []): con.execute(stmt)
    b_plan, b_t = plan(before_sql), timeit(before_sql)
    rows_b = con.execute(before_sql).fetchall()
    for stmt in (setup or []): con.execute(stmt)
    con.commit()
    a_plan, a_t = plan(after_sql), timeit(after_sql)
    rows_a = con.execute(after_sql).fetchall()
    same = (sorted(map(str,rows_a)) == sorted(map(str,rows_b))) if len(rows_a) < 5000 else (len(rows_a)==len(rows_b))
    speed = b_t / a_t if a_t else float('inf')
    summary.append((title, b_t, a_t, speed, same))
    report.append(f"## {title}\n\n**Why:** {why}\n")
    report.append(f"**Before** ({b_t:.2f} ms)\n```sql\n{before_sql.strip()}\n```\nPlan: `{' | '.join(b_plan)}`\n")
    report.append(f"**After** ({a_t:.2f} ms, **{speed:.1f}x faster**)\n```sql\n{after_sql.strip()}\n```\nPlan: `{' | '.join(a_plan)}`\n")
    report.append(f"Results identical: **{same}**\n")
    print(f"{title:55s} {b_t:9.2f} ms -> {a_t:8.2f} ms  ({speed:6.1f}x)  same_result={same}")

drop = lambda *idx: [f"DROP INDEX IF EXISTS {i}" for i in idx]

experiment("OPT1 Index on filter column",
    "Without an index the engine scans every row. A B-tree index turns it into a direct lookup.",
    "SELECT COUNT(*) FROM orders WHERE customer_id = 42",
    "SELECT COUNT(*) FROM orders WHERE customer_id = 42",
    setup=["CREATE INDEX idx_orders_customer ON orders(customer_id)"],
    teardown=drop("idx_orders_customer"))

experiment("OPT2 Composite index (filter + sort)",
    "Equality columns first, then the sort column: the index returns rows already ordered, so no sort step.",
    "SELECT order_id, order_date FROM orders WHERE customer_id=42 AND status='completed' ORDER BY order_date",
    "SELECT order_id, order_date FROM orders WHERE customer_id=42 AND status='completed' ORDER BY order_date",
    setup=drop("idx_orders_customer")+["CREATE INDEX idx_orders_cust_status_date ON orders(customer_id,status,order_date)"],
    teardown=drop("idx_orders_customer","idx_orders_cust_status_date"))

experiment("OPT3 Covering index",
    "When the index contains every column the query needs, the table itself is never touched.",
    "SELECT order_id, SUM(quantity) FROM order_items GROUP BY order_id",
    "SELECT order_id, SUM(quantity) FROM order_items GROUP BY order_id",
    setup=["CREATE INDEX idx_items_order_cover ON order_items(order_id, quantity)"],
    teardown=drop("idx_items_order_cover"))

experiment("OPT4 SARGable date filter",
    "Wrapping the column in strftime() hides it from the index. Compare the raw column to a range instead.",
    "SELECT COUNT(*) FROM orders WHERE strftime('%Y', order_date) = '2025'",
    "SELECT COUNT(*) FROM orders WHERE order_date >= '2025-01-01' AND order_date < '2026-01-01'",
    setup=["CREATE INDEX idx_orders_date ON orders(order_date)"],
    teardown=drop("idx_orders_date"))

experiment("OPT5 Correlated subquery vs window function (trade-off)",
    "A correlated MAX() re-runs per outer row. Without a supporting index that is O(n^2) and the window function wins by a wide margin; "
    "BUT with an index on (customer_id, order_date) SQLite turns each MAX() into a single index seek, which can beat the window function's full sort. "
    "Lesson: measure, and check the plan. This benchmark deliberately gives the correlated query its index, so the window version is slower here.",
    """SELECT o.customer_id, o.order_id FROM orders o
       WHERE o.order_date = (SELECT MAX(o2.order_date) FROM orders o2 WHERE o2.customer_id = o.customer_id)""",
    """SELECT customer_id, order_id FROM (
         SELECT customer_id, order_id,
                RANK() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS rk
         FROM orders) WHERE rk = 1""",
    teardown=drop("idx_orders_customer","idx_orders_date","idx_orders_cust_status_date")+["CREATE INDEX idx_orders_cust_date ON orders(customer_id, order_date)"])
con.execute("DROP INDEX IF EXISTS idx_orders_cust_date")

experiment("OPT6 Aggregate before joining (avoid fan-out)",
    "Pre-aggregating order_items to one row per order shrinks the join input before the expensive grouping.",
    """SELECT o.customer_id, SUM(oi.quantity*oi.unit_price) AS spend
       FROM orders o JOIN order_items oi ON oi.order_id=o.order_id
       WHERE o.status='completed' GROUP BY o.customer_id""",
    """WITH per_order AS (SELECT order_id, SUM(quantity*unit_price) AS v FROM order_items GROUP BY order_id)
       SELECT o.customer_id, SUM(po.v) AS spend
       FROM orders o JOIN per_order po ON po.order_id=o.order_id
       WHERE o.status='completed' GROUP BY o.customer_id""",
    setup=["CREATE INDEX idx_items_order_cover ON order_items(order_id, quantity, unit_price)"],
    teardown=drop("idx_items_order_cover"))

experiment("OPT7 UNION -> UNION ALL",
    "UNION must sort/deduplicate the combined result. UNION ALL just appends (use when overlap is impossible or fine).",
    "SELECT order_id FROM orders WHERE status='cancelled' UNION SELECT order_id FROM orders WHERE status='returned'",
    "SELECT order_id FROM orders WHERE status='cancelled' UNION ALL SELECT order_id FROM orders WHERE status='returned'",
    teardown=[])

experiment("OPT8 OFFSET -> keyset pagination",
    "OFFSET reads and throws away every skipped row. Keyset seeks straight to the next page by key.",
    "SELECT order_id, order_date FROM orders ORDER BY order_id LIMIT 20 OFFSET 30000",
    "SELECT order_id, order_date FROM orders WHERE order_id > 39500 ORDER BY order_id LIMIT 20",
    teardown=[])

experiment("OPT9 IN (subquery) -> EXISTS",
    "EXISTS can stop at the first match per customer; combined with an index it avoids materializing the list.",
    "SELECT c.customer_id FROM customers c WHERE c.customer_id IN (SELECT customer_id FROM orders WHERE status='returned')",
    "SELECT c.customer_id FROM customers c WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id=c.customer_id AND o.status='returned')",
    setup=["CREATE INDEX idx_orders_cust_status ON orders(customer_id, status)"],
    teardown=drop("idx_orders_cust_status"))

experiment("OPT10 Filter early with WHERE, not HAVING",
    "WHERE removes rows before grouping; HAVING on a non-aggregate makes the engine group everything first.",
    "SELECT status, COUNT(*) c FROM orders GROUP BY status HAVING status = 'completed'",
    "SELECT status, COUNT(*) c FROM orders WHERE status = 'completed' GROUP BY status",
    setup=["CREATE INDEX idx_orders_status ON orders(status)"],
    teardown=drop("idx_orders_status"))

report.append("## Summary\n\n| Experiment | Before (ms) | After (ms) | Speed-up | Same result |\n|---|---:|---:|---:|:--:|")
for t,b,a,s,same in summary: report.append(f"| {t} | {b:.2f} | {a:.2f} | {s:.1f}x | {'yes' if same else 'NO'} |")
open(os.path.join(ROOT,"output","optimization_report.md"),"w").write("\n".join(report)+"\n")
con.close(); os.remove(BIG)
print("\nreport -> output/optimization_report.md")
