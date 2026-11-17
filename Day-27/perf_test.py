"""Performance test: baseline (row-by-row) vs optimized pipeline, query index test, parallel validation."""
import os, re, sqlite3, tempfile, time
from multiprocessing import Pool
import pandas as pd
from generate_data import generate
from pipeline import run, validate

d = tempfile.mkdtemp()
timeit = lambda f: (lambda t: (f(), time.time() - t)[1])(time.time())


def baseline(csv, db):
    """Naive version: python loop per row, no primary key/index, insert one row at a time."""
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE orders(order_id, customer_id, email, amount, order_date, status)")
    for r in pd.read_csv(csv, dtype=str, keep_default_na=False).to_dict("records"):
        try:
            ok = (r["order_id"] and float(r["amount"]) > 0 and re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", r["email"])
                  and r["status"] in ("new", "paid", "shipped", "cancelled"))
        except ValueError:
            ok = False
        if ok:
            con.execute("INSERT INTO orders VALUES(?,?,?,?,?,?)", tuple(r.values()))
            con.commit()
    con.close()


def val_chunk(c):
    return len(validate(c)[0])


rows = []
for n in [10_000, 100_000, 1_000_000]:
    csv = f"{d}/o{n}.csv"
    generate(n).drop(columns="bad_reason").to_csv(csv, index=False)
    t_base = timeit(lambda: baseline(csv, f"{d}/b{n}.db")) if n <= 100_000 else None
    t_opt = timeit(lambda: run(csv, f"{d}/p{n}.db"))
    rows.append((n, t_base, t_opt))
    print(f"{n:>9,} rows | baseline {t_base and round(t_base, 2)} s | optimized {t_opt:.2f} s | {n / t_opt:,.0f} rows/s", flush=True)

# index test on the 1M-row table
con = sqlite3.connect(f"{d}/p1000000.db")
q = "SELECT COUNT(*), SUM(amount) FROM orders WHERE order_date = '2025-06-15'"
t_idx = timeit(lambda: con.execute(q).fetchall())
con.execute("DROP INDEX idx_orders_date")
t_no = timeit(lambda: con.execute(q).fetchall())
print(f"date query on 1M rows | with index {t_idx * 1000:.1f} ms | without {t_no * 1000:.1f} ms")

# parallel validation test (validation step only, 1M rows)
df = pd.read_csv(f"{d}/o1000000.csv", dtype=str, keep_default_na=False)
chunks = [df.iloc[i:i + 125_000] for i in range(0, len(df), 125_000)]
t_serial = timeit(lambda: [val_chunk(c) for c in chunks])
with Pool(4) as p:
    t_par = timeit(lambda: p.map(val_chunk, chunks))
print(f"validate 1M rows | serial {t_serial:.2f} s | 4 processes {t_par:.2f} s")
