"""Simple pipeline: CSV -> validate -> SQLite. Good rows are upserted, bad rows go to `rejects`."""
import re
import sqlite3
import pandas as pd

VALID_STATUS = ["new", "paid", "shipped", "cancelled"]


def validate(df, seen=()):
    """df: all-string DataFrame; seen: order_ids from earlier chunks. Returns (good_df, bad_df with `reason`)."""
    amount = pd.to_numeric(df["amount"], errors="coerce")
    date = pd.to_datetime(df["order_date"], format="%Y-%m-%d", errors="coerce")
    checks = [
        ("null_order_id", df["order_id"].isna() | (df["order_id"].str.strip() == "")),
        ("duplicate_order_id", df["order_id"].duplicated(keep="first") | df["order_id"].isin(seen)),
        ("bad_amount", amount.isna() | (amount <= 0) | (amount > 100000)),
        ("bad_email", ~df["email"].fillna("").str.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")),
        ("bad_date", date.isna() | (date > pd.Timestamp.today())),
        ("bad_status", ~df["status"].isin(VALID_STATUS)),
    ]
    reason = pd.Series("", index=df.index)
    for name, bad in checks:                      # first failing rule wins
        reason[bad & (reason == "")] = name
    good = df[reason == ""].copy()
    good["amount"] = amount[good.index]
    bad = df[reason != ""].copy()
    bad["reason"] = reason[bad.index]
    return good, bad


def connect(db):
    con = sqlite3.connect(db)
    con.execute("""CREATE TABLE IF NOT EXISTS orders(
        order_id TEXT PRIMARY KEY, customer_id TEXT, email TEXT,
        amount REAL, order_date TEXT, status TEXT)""")
    con.execute("CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date)")
    con.execute("""CREATE TABLE IF NOT EXISTS rejects(
        order_id TEXT, customer_id TEXT, email TEXT, amount TEXT,
        order_date TEXT, status TEXT, reason TEXT)""")
    return con


def run(csv_path, db, chunksize=100_000):
    """Process the file in chunks. Re-running is safe (upsert), so incremental loads just work."""
    con = connect(db)
    total = ok = rejected = 0
    seen = set()                                  # catches duplicates that span chunks
    for chunk in pd.read_csv(csv_path, dtype=str, keep_default_na=False, chunksize=chunksize):
        good, bad = validate(chunk, seen)
        seen.update(good["order_id"])
        con.executemany("INSERT OR REPLACE INTO orders VALUES(?,?,?,?,?,?)", good.itertuples(index=False, name=None))
        con.executemany("INSERT INTO rejects VALUES(?,?,?,?,?,?,?)", bad.itertuples(index=False, name=None))
        total, ok, rejected = total + len(chunk), ok + len(good), rejected + len(bad)
    con.commit()
    con.close()
    return {"total": total, "loaded": ok, "rejected": rejected}
