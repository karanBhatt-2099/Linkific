
import argparse
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_sample_data import generate  # noqa: E402
from etl.config import VALID_STATUSES  # noqa: E402
from etl.transform import transform_orders  # noqa: E402


def naive_transform(raw: pd.DataFrame) -> pd.DataFrame:
    seen, out = {}, []
    for _, r in raw.iterrows():
        try:
            oid = (r["order_id"] or "").strip()
            cust = r["customer_id"]
            qty = float(r["quantity"])
            price = float(r["unit_price"])
            date = pd.to_datetime(r["order_date"]).date()
            status = (r["status"] or "").strip().lower()
        except (ValueError, TypeError, AttributeError):
            continue
        if not oid or pd.isna(cust) or qty <= 0 or qty % 1 or price < 0 or status not in VALID_STATUSES:
            continue
        seen[oid] = {"order_id": oid, "quantity": int(qty), "unit_price": price, "order_date": date,
                     "status": status, "gross_amount": round(qty * price, 2)}
    return pd.DataFrame(list(seen.values()))


def timed(fn, *a):
    t = time.perf_counter()
    res = fn(*a)
    return res, time.perf_counter() - t


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=100_000)
    n = ap.parse_args().rows
    raw = generate(n, 0.02)
    naive, t_naive = timed(naive_transform, raw)
    (opt, _rej), t_opt = timed(transform_orders, raw)
    assert len(naive) == len(opt), f"outputs differ: {len(naive)} vs {len(opt)}"
    print(f"rows in: {len(raw):,}  clean rows (both): {len(opt):,}")
    print(f"naive row-by-row : {t_naive:7.2f}s")
    print(f"vectorised       : {t_opt:7.2f}s")
    print(f"speed-up         : {t_naive / t_opt:7.0f}x")
