
import argparse
import random
from pathlib import Path

import pandas as pd

PRODUCTS = {
    "Electronics": [("Headphones", 59.99), ("Phone Case", 12.5), ("Charger", 19.0), ("Smart Watch", 149.0)],
    "Home": [("Desk Lamp", 29.9), ("Cushion", 14.0), ("Kettle", 34.5)],
    "Books": [("Data Engineering Book", 42.0), ("SQL Cookbook", 35.0)],
    "Fitness": [("Yoga Mat", 25.0), ("Dumbbells", 55.0)],
}
COUNTRIES = ["IN", "US", "GB", "DE", "SG"]
STATUSES = ["completed"] * 7 + ["pending", "cancelled", "refunded"]


def generate(rows: int, dirty: float, seed: int = 42) -> pd.DataFrame:
    rnd = random.Random(seed)
    recs = []
    for i in range(1, rows + 1):
        cat = rnd.choice(list(PRODUCTS))
        prod, price = rnd.choice(PRODUCTS[cat])
        recs.append({
            "order_id": f"ORD{i:07d}",
            "customer_id": f"C{rnd.randint(1, max(rows // 5, 10)):05d}",
            "product": prod, "category": cat,
            "quantity": rnd.randint(1, 5), "unit_price": price,
            "order_date": f"2026-{rnd.randint(9, 11):02d}-{rnd.randint(1, 28):02d}",
            "status": rnd.choice(STATUSES), "country": rnd.choice(COUNTRIES),
        })
    df = pd.DataFrame(recs).astype(str)

    # Inject problems
    n_bad = int(rows * dirty)
    idx = rnd.sample(range(rows), min(n_bad * 4, rows))
    chunks = [idx[i::4] for i in range(4)]
    df.loc[chunks[0], "quantity"] = "-1"                     # invalid quantity
    df.loc[chunks[1], "order_date"] = "not-a-date"           # invalid date
    df.loc[chunks[2], "status"] = "  COMPLETED "             # fixable: whitespace/case
    df.loc[chunks[3][: len(chunks[3]) // 2], "customer_id"] = ""   # missing customer
    df = pd.concat([df, df.sample(n_bad, random_state=seed)], ignore_index=True)  # exact duplicates
    return df.sample(frac=1, random_state=seed).reset_index(drop=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=1000)
    ap.add_argument("--out", default="data/raw/orders.csv")
    ap.add_argument("--dirty", type=float, default=0.02)
    a = ap.parse_args()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    generate(a.rows, a.dirty).to_csv(out, index=False)
    print(f"Wrote {out}")
