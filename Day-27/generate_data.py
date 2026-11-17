"""Synthetic order data with labelled bad rows (ground truth for testing the checks)."""
import sys
import numpy as np
import pandas as pd

BAD_KINDS = ["null_order_id", "duplicate_order_id", "bad_amount", "bad_email", "bad_date", "bad_status"]


def generate(n, bad_rate=0.05, seed=42, start_id=1):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "order_id": [f"O{i}" for i in range(start_id, start_id + n)],
        "customer_id": rng.integers(1, max(n // 10, 2), n).astype(str),
        "email": [f"user{i}@example.com" for i in rng.integers(1, 100000, n)],
        "amount": rng.uniform(1, 500, n).round(2).astype(str),
        "order_date": (pd.Timestamp("2025-01-01") + pd.to_timedelta(rng.integers(0, 300, n), unit="D")).strftime("%Y-%m-%d"),
        "status": rng.choice(["new", "paid", "shipped", "cancelled"], n),
    })
    df["bad_reason"] = ""

    # inject bad rows: pick rows at random, assign each a defect (edge cases included)
    bad_idx = rng.choice(n, int(n * bad_rate), replace=False)
    kinds = rng.choice(BAD_KINDS, len(bad_idx))
    for i, k in zip(bad_idx, kinds):
        if k == "null_order_id":
            df.at[i, "order_id"] = ""
        elif k == "duplicate_order_id" and i > 0:
            df.at[i, "order_id"] = df.at[i - 1, "order_id"] if df.at[i - 1, "bad_reason"] == "" else "O0"
        elif k == "bad_amount":
            df.at[i, "amount"] = rng.choice(["-5", "0", "abc", "", "999999999"])
        elif k == "bad_email":
            df.at[i, "email"] = rng.choice(["no-at-sign", "a@b", "", "@x.com", "a b@c.com"])
        elif k == "bad_date":
            df.at[i, "order_date"] = rng.choice(["2099-01-01", "2025-13-45", "not-a-date", ""])
        elif k == "bad_status":
            df.at[i, "status"] = "unknown"
        else:
            continue
        df.at[i, "bad_reason"] = k
    return df


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    df = generate(n)
    df.drop(columns="bad_reason").to_csv("orders.csv", index=False)
    df[["order_id", "bad_reason"]].to_csv("orders_truth.csv", index=False)
    print(f"wrote orders.csv with {n} rows, {(df.bad_reason != '').sum()} bad")
