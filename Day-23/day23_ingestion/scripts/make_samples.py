"""Create sample input files + a source SQLite DB.
   python scripts/make_samples.py          -> first-time setup (200 orders, csv/json/xlsx files)
   python scripts/make_samples.py update   -> change 5 orders + add 5 (to demo the incremental load)"""
import random
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
FMT = "%Y-%m-%d %H:%M:%S"
now = datetime.utcnow()

(DATA / "input").mkdir(parents=True, exist_ok=True)
db = sqlite3.connect(DATA / "source.db")
db.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, customer TEXT, "
           "amount REAL, status TEXT, updated_at TEXT)")


def new_orders(start, n, when):
    return [(start + i, f"customer_{random.randint(1, 50)}", round(random.uniform(10, 500), 2),
             "new", when(i).strftime(FMT)) for i in range(n)]


if len(sys.argv) > 1 and sys.argv[1] == "update":
    db.execute("UPDATE orders SET status='shipped', updated_at=? WHERE id <= 5", (now.strftime(FMT),))
    last_id = db.execute("SELECT MAX(id) FROM orders").fetchone()[0]
    db.executemany("INSERT INTO orders VALUES (?,?,?,?,?)", new_orders(last_id + 1, 5, lambda i: now))
else:
    db.executemany("INSERT OR IGNORE INTO orders VALUES (?,?,?,?,?)",
                   new_orders(1, 200, lambda i: now - timedelta(days=random.randint(1, 60))))
    pd.DataFrame({"id": range(1, 501), "name": [f"User {i}" for i in range(1, 501)],
                  "city": random.choices(["Mumbai", "Pune", "Delhi", "Bengaluru"], k=500)}
                 ).to_csv(DATA / "input" / "customers.csv", index=False)
    pd.DataFrame({"sku": [f"P{i}" for i in range(20)], "price": [round(random.uniform(5, 99), 2) for _ in range(20)]}
                 ).to_json(DATA / "input" / "products.json", orient="records")
    pd.DataFrame({"order_id": range(50), "qty": [random.randint(1, 9) for _ in range(50)]}
                 ).to_excel(DATA / "input" / "sales.xlsx", index=False)
db.commit()
print("Sample data ready in", DATA)
