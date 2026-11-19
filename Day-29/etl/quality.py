"""Data-quality checks: pure-pandas (pre-load) and SQL (post-load)."""
import pandas as pd

from etl.snowflake_client import run_sql


class DataQualityError(AssertionError):
    pass


def check_dataframe(clean: pd.DataFrame, rejects: pd.DataFrame, raw_rows: int,
                    max_reject_ratio: float = 0.20) -> dict:
    """Pre-load checks. Raises DataQualityError on failure, returns metrics otherwise."""
    problems = []
    if clean.empty:
        problems.append("no valid rows after transform")
    if clean["order_id"].duplicated().any():
        problems.append("duplicate order_id in clean data")
    if clean[["order_id", "customer_id", "order_date"]].isna().any().any():
        problems.append("nulls in key columns")
    if (clean["quantity"] <= 0).any() or (clean["unit_price"] < 0).any():
        problems.append("non-positive quantity or negative price")
    if len(clean) + len(rejects) != raw_rows:
        problems.append(f"row reconciliation failed: {len(clean)}+{len(rejects)} != {raw_rows}")
    ratio = len(rejects) / raw_rows if raw_rows else 1.0
    if ratio > max_reject_ratio:
        problems.append(f"reject ratio {ratio:.1%} exceeds {max_reject_ratio:.0%}")
    if problems:
        raise DataQualityError("; ".join(problems))
    return {"raw_rows": raw_rows, "clean_rows": len(clean), "reject_rows": len(rejects),
            "reject_ratio": round(ratio, 4)}


def check_snowflake(conn, batch_id: str, expected_rows: int) -> dict:
    """Post-load checks against Snowflake."""
    problems = []
    staged = run_sql(conn, "SELECT COUNT(*) FROM RAW.ORDERS_STG WHERE BATCH_ID = %s", (batch_id,))[0][0]
    if staged != expected_rows:
        problems.append(f"staging rows {staged} != expected {expected_rows}")

    dupes = run_sql(conn, "SELECT COUNT(*) FROM (SELECT ORDER_ID FROM CORE.ORDERS "
                          "GROUP BY ORDER_ID HAVING COUNT(*) > 1)")[0][0]
    if dupes:
        problems.append(f"{dupes} duplicated order_id in CORE.ORDERS")

    nulls = run_sql(conn, "SELECT COUNT(*) FROM CORE.ORDERS WHERE ORDER_ID IS NULL "
                          "OR CUSTOMER_ID IS NULL OR ORDER_DATE IS NULL")[0][0]
    if nulls:
        problems.append(f"{nulls} rows with null keys in CORE.ORDERS")

    # Mart must reconcile with core
    core_rev = run_sql(conn, "SELECT COALESCE(SUM(NET_REVENUE),0) FROM CORE.ORDERS")[0][0]
    mart_rev = run_sql(conn, "SELECT COALESCE(SUM(NET_REVENUE),0) FROM MART.DAILY_SALES")[0][0]
    if abs(float(core_rev) - float(mart_rev)) > 0.01:
        problems.append(f"mart revenue {mart_rev} != core revenue {core_rev}")

    if problems:
        raise DataQualityError("; ".join(problems))
    return {"staged": staged, "core_revenue": float(core_rev), "mart_revenue": float(mart_rev)}
