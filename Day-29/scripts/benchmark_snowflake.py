
import csv
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from etl.snowflake_client import get_connection, run_sql  # noqa: E402

QUERIES = {
    "mart_revenue_by_day": "SELECT ORDER_DATE, SUM(NET_REVENUE) FROM MART.DAILY_SALES GROUP BY 1 ORDER BY 1",
    "mart_top_categories": "SELECT CATEGORY, SUM(NET_REVENUE) r FROM MART.DAILY_SALES GROUP BY 1 ORDER BY r DESC",
    "core_revenue_by_day (no mart)": "SELECT ORDER_DATE, SUM(NET_REVENUE) FROM CORE.ORDERS GROUP BY 1 ORDER BY 1",
}

if __name__ == "__main__":
    out = Path("docs/benchmark_results.csv")
    new = not out.exists()
    with get_connection() as conn, out.open("a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["run_at", "query", "seconds"])
        for name, sql in QUERIES.items():
            t = time.perf_counter()
            run_sql(conn, sql)
            dt = round(time.perf_counter() - t, 3)
            w.writerow([datetime.now().isoformat(timespec="seconds"), name, dt])
            print(f"{name:35s} {dt}s")
