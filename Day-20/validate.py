"""Validate data quality: row counts, orphan foreign keys, logical rules."""
import psycopg2
from config import *

# (database, description, SQL returning ONE number that should be 0)
CHECKS = [
    ("ecommerce_db", "orders without a customer",
     "SELECT COUNT(*) FROM orders o LEFT JOIN customers c USING(customer_id) WHERE c.customer_id IS NULL"),
    ("ecommerce_db", "order_items without a product",
     "SELECT COUNT(*) FROM order_items i LEFT JOIN products p USING(product_id) WHERE p.product_id IS NULL"),
    ("ecommerce_db", "orders placed before customer signup",
     "SELECT COUNT(*) FROM orders o JOIN customers c USING(customer_id) WHERE o.order_date < c.created_at"),
    ("ecommerce_db", "order total != sum of items",
     "SELECT COUNT(*) FROM orders o JOIN (SELECT order_id, SUM(quantity*unit_price) s FROM order_items GROUP BY order_id) i "
     "USING(order_id) WHERE ABS(o.total_amount - i.s) > 0.01"),
    ("hr_db", "employees with missing department",
     "SELECT COUNT(*) FROM employees e LEFT JOIN departments d USING(dept_id) WHERE d.dept_id IS NULL"),
    ("hr_db", "attendance before hire date",
     "SELECT COUNT(*) FROM attendance a JOIN employees e USING(emp_id) WHERE a.work_date < e.hire_date"),
    ("hr_db", "employees hired before their manager",
     "SELECT COUNT(*) FROM employees e JOIN employees m ON e.manager_id = m.emp_id WHERE e.hire_date < m.hire_date"),
    ("finance_db", "transactions before account opened",
     "SELECT COUNT(*) FROM transactions t JOIN accounts a USING(account_id) WHERE t.txn_date < a.opened_date"),
    ("finance_db", "negative balances",
     "SELECT COUNT(*) FROM transactions WHERE balance_after < 0"),
    ("finance_db", "account balance != last transaction balance",
     "SELECT COUNT(*) FROM accounts a JOIN (SELECT DISTINCT ON (account_id) account_id, balance_after FROM transactions "
     "ORDER BY account_id, txn_id DESC) t USING(account_id) WHERE a.balance <> t.balance_after"),
]

for db, tables in DATABASES.items():
    conn = psycopg2.connect(dbname=db, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    cur = conn.cursor()
    print(f"\n=== {db} ===")
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        print(f"  {t:<14} {cur.fetchone()[0]:>10,} rows")
    for d, text, sql in CHECKS:
        if d == db:
            cur.execute(sql)
            bad = cur.fetchone()[0]
            print(f"  [{'PASS' if bad == 0 else 'FAIL'}] {text}: {bad}")
    conn.close()
