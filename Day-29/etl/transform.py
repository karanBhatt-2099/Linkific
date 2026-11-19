"""Transform: clean, type, validate and derive columns. Fully vectorised (no row loops)."""
import pandas as pd

from etl.config import VALID_STATUSES


def transform_orders(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (clean, rejects). Every input row lands in exactly one of them,
    except duplicate order_ids, which are dropped (last occurrence wins) and counted
    in rejects with reason 'duplicate_order_id'."""
    df = raw.copy()

    # 1. Normalise text
    for col in ["order_id", "customer_id", "product", "category", "status", "country"]:
        df[col] = df[col].astype("string").str.strip()
    df["status"] = df["status"].str.lower()
    df["country"] = df["country"].str.upper()
    df["category"] = df["category"].str.title()

    # 2. Type conversion (bad values become NaN/NaT instead of raising)
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce").dt.date

    # 3. Validation -> reject reason (first failing rule wins)
    reason = pd.Series(pd.NA, index=df.index, dtype="string")

    def flag(mask, text):
        nonlocal reason
        reason = reason.mask(mask & reason.isna(), text)

    flag(df["order_id"].isna() | (df["order_id"] == ""), "missing_order_id")
    flag(df["customer_id"].isna(), "missing_customer_id")
    flag(df["quantity"].isna() | (df["quantity"] <= 0) | (df["quantity"] % 1 != 0), "invalid_quantity")
    flag(df["unit_price"].isna() | (df["unit_price"] < 0), "invalid_unit_price")
    flag(pd.isna(df["order_date"]), "invalid_order_date")
    flag(~df["status"].isin(VALID_STATUSES), "invalid_status")

    rejects = df[reason.notna()].copy()
    rejects["reject_reason"] = reason[reason.notna()]
    good = df[reason.isna()].copy()

    # 4. Deduplicate on business key (keep last = latest record in file)
    dupes_mask = good.duplicated(subset="order_id", keep="last")
    dupes = good[dupes_mask].copy()
    dupes["reject_reason"] = "duplicate_order_id"
    good = good[~dupes_mask]
    rejects = pd.concat([rejects, dupes], ignore_index=True)

    # 5. Derived columns
    good["quantity"] = good["quantity"].astype("int64")
    good["unit_price"] = good["unit_price"].astype("float64").round(2)
    good["gross_amount"] = (good["quantity"] * good["unit_price"]).round(2)
    good["net_revenue"] = good["gross_amount"].where(good["status"] == "completed", 0.0)
    good["country"] = good["country"].fillna("UNKNOWN")
    good["category"] = good["category"].fillna("Uncategorized")
    good["product"] = good["product"].fillna("Unknown")

    return good.reset_index(drop=True), rejects.reset_index(drop=True)
