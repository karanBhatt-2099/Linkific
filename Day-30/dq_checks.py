"""Step 4: Simple data quality checks. Raises an error if any check fails."""
from snowflake_conn import get_connection

# Each check: (name, SQL returning a number, rule on that number)
CHECKS = [
    ("row_count > 0",
     "SELECT COUNT(*) FROM RAW.PRODUCTS", lambda x: x > 0),
    ("no null id/price/category",
     "SELECT COUNT(*) FROM RAW.PRODUCTS WHERE id IS NULL OR price IS NULL OR category IS NULL",
     lambda x: x == 0),
    ("no duplicate ids",
     "SELECT COUNT(*) - COUNT(DISTINCT id) FROM RAW.PRODUCTS", lambda x: x == 0),
    ("price > 0 and stock >= 0",
     "SELECT COUNT(*) FROM RAW.PRODUCTS WHERE price <= 0 OR stock < 0", lambda x: x == 0),
]


def run_checks():
    conn = get_connection()
    cur = conn.cursor()
    failed = []
    try:
        for name, sql, rule in CHECKS:
            value = cur.execute(sql).fetchone()[0]
            ok = rule(value)
            print(f"[{'PASS' if ok else 'FAIL'}] {name} (value={value})")
            if not ok:
                failed.append(name)
    finally:
        cur.close()
        conn.close()

    if failed:
        raise ValueError(f"Data quality checks failed: {failed}")
    print("All data quality checks passed")


if __name__ == "__main__":
    run_checks()
