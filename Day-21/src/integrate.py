"""Integration: schema mapping, key matching, merge, conflict handling, lineage."""
from datetime import datetime, timezone

import pandas as pd

from src.load_snowflake import connect, load_df
from src.utils import log, read_raw
import os

# ---- 1. SCHEMA MAPPING: source column -> unified column ----
UNIFIED = ["email", "name", "phone", "city", "loyalty_tier", "updated_at"]
MAPPINGS = {                        # order = PRIORITY (first source wins a conflict)
    "pg_customers":   {"name": "name", "email": "email", "city": "city", "updated_at": "updated_at"},
    "sftp_customers": {"name": "name", "email": "email", "city": "city", "loyalty_tier": "loyalty_tier"},
    "csv_customers":  {"full_name": "name", "email": "email", "phone": "phone", "city": "city",
                       "updated_at": "updated_at"},
    "api_users":      {"name": "name", "email": "email", "phone": "phone", "city": "city"},
}


def build_customers():
    frames, lineage = [], []
    for rank, (src, mapping) in enumerate(MAPPINGS.items()):
        df = read_raw(src).rename(columns=mapping).reindex(columns=UNIFIED)
        # ---- 2. KEY MATCHING: normalised email is the common key ----
        df["email"] = df["email"].str.lower().str.strip()
        df["updated_at"] = pd.to_datetime(df["updated_at"], errors="coerce")
        df["_source"], df["_rank"] = src, rank
        frames.append(df.dropna(subset=["email"]))
        lineage.append({"target": "customers_gold", "source": src, "rows_in": len(df)})
    all_rows = pd.concat(frames).sort_values("_rank")

    # ---- 4. CONFLICTS: same email, different values for a column ----
    conflicts = []
    for col in ["name", "phone", "city", "loyalty_tier"]:
        values = all_rows.dropna(subset=[col]).groupby("email")[col].agg(lambda s: list(dict.fromkeys(s)))
        for email, vals in values.items():
            if len(vals) > 1:
                conflicts.append({"email": email, "column_name": col,
                                  "all_values": " | ".join(vals), "chosen_value": vals[0]})

    # ---- 3. MERGE STRATEGY: highest-priority source wins; gaps filled from lower ones ----
    agg = {c: "first" for c in ["name", "phone", "city", "loyalty_tier"]}  # 'first' skips nulls
    agg["updated_at"] = "max"
    agg["_source"] = lambda s: ",".join(dict.fromkeys(s))
    gold = all_rows.groupby("email", as_index=False).agg(agg).rename(columns={"_source": "sources"})
    return gold, pd.DataFrame(conflicts), lineage


def build_orders():
    cols = ["order_id", "email", "amount", "order_date"]
    # key matching: postgres orders have customer_id -> join to get email
    pg = read_raw("pg_orders").merge(read_raw("pg_customers")[["customer_id", "email"]],
                                     on="customer_id", how="left")
    js = read_raw("file_orders").rename(columns={"customer_email": "email"})
    pg, js = pg[cols].assign(source="pg_orders"), js[cols].assign(source="file_orders")
    # dedupe on order_id: postgres listed first, so it wins
    orders = pd.concat([pg, js]).drop_duplicates("order_id", keep="first")
    orders["email"] = orders["email"].str.lower()
    orders["order_date"] = pd.to_datetime(orders["order_date"]).dt.date
    lineage = [{"target": "orders_gold", "source": "pg_orders", "rows_in": len(pg)},
               {"target": "orders_gold", "source": "file_orders", "rows_in": len(js)}]
    return orders, lineage


def run():
    customers, conflicts, lin1 = build_customers()
    orders, lin2 = build_orders()
    run_ts = datetime.now(timezone.utc).isoformat()
    lineage = pd.DataFrame(lin1 + lin2).assign(run_ts=run_ts)
    log.info("customers_gold=%s orders_gold=%s conflicts=%s",
             len(customers), len(orders), len(conflicts))

    schema = os.getenv("SNOWFLAKE_SCHEMA_ANALYTICS", "ANALYTICS")
    conn = connect()
    try:
        load_df(conn, customers, "customers_gold", schema)
        load_df(conn, orders, "orders_gold", schema)
        load_df(conn, lineage, "data_lineage", schema)
        if len(conflicts):
            load_df(conn, conflicts, "customer_conflicts", schema)
    finally:
        conn.close()
