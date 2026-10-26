import numpy as np
import pandas as pd

from src.utils.logger import get_logger

log = get_logger("transform")


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["customer_id"] = df["customer_id"].astype(int)
    df["customer_name"] = df["customer_name"].str.strip().str.title()
    df["email"] = df["email"].str.strip().str.lower()
    df["city"] = df["city"].str.strip().str.title()
    df["updated_at"] = pd.to_datetime(df["updated_at"])
    df = df.drop_duplicates("customer_id", keep="last")
    return df[["customer_id", "customer_name", "email", "city", "updated_at"]]


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if df.empty:
        return df
    df["order_id"] = df["order_id"].astype(int)
    df["customer_id"] = df["customer_id"].astype(int)
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["order_status"] = df["status"].str.strip().str.upper()
    df["updated_at"] = pd.to_datetime(df["updated_at"])
    df = df.drop_duplicates("order_id", keep="last")
    return df[["order_id", "customer_id", "order_date", "order_status", "updated_at"]]


def clean_order_items(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        df[col] = df[col].str.strip()
    for col in ["order_item_id", "order_id", "product_id", "quantity", "discount_pct"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["discount_pct"] = df["discount_pct"].fillna(0)

    before = len(df)
    df = df.dropna(subset=["order_item_id", "order_id", "product_id", "quantity"])
    df = df[df["quantity"] > 0]
    df = df.drop_duplicates("order_item_id", keep="last")
    log.info("order_items: dropped %d invalid/duplicate rows", before - len(df))

    for col in ["order_item_id", "order_id", "product_id", "quantity"]:
        df[col] = df[col].astype(int)
    return df


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={"id": "product_id", "title": "product_name", "price": "unit_price"}).copy()
    df["product_id"] = df["product_id"].astype(int)
    df["product_name"] = df["product_name"].str.strip()
    df["category"] = df["category"].str.replace("-", " ").str.title()
    df["brand"] = df["brand"].fillna("Unknown").str.strip()
    df["unit_price"] = df["unit_price"].astype(float).round(2)
    df = df.drop_duplicates("product_id")
    return df[["product_id", "product_name", "category", "brand", "unit_price"]]


FACT_COLUMNS = [
    "order_item_id", "order_id", "order_date", "customer_id", "customer_city",
    "product_id", "product_category", "quantity", "unit_price", "discount_pct",
    "gross_amount", "discount_amount", "net_amount",
    "order_status", "order_value_tier", "updated_at",
]


def build_fact_sales(orders, items, customers, products) -> pd.DataFrame:
    """Join order_items (CSV) + orders (Postgres) + customers (Postgres) + products (API)."""
    if orders.empty:
        return pd.DataFrame(columns=FACT_COLUMNS)

    fact = (
        items.merge(orders, on="order_id", how="inner")
        .merge(customers[["customer_id", "city"]].rename(columns={"city": "customer_city"}),
               on="customer_id", how="left")
        .merge(products[["product_id", "category", "unit_price"]]
               .rename(columns={"category": "product_category"}),
               on="product_id", how="left")
    )

    unknown = fact["unit_price"].isna().sum()
    if unknown:
        log.warning("Dropping %d order items with unknown product", unknown)
    fact = fact.dropna(subset=["unit_price"])

    # Business logic
    fact["gross_amount"] = (fact["quantity"] * fact["unit_price"]).round(2)
    fact["discount_amount"] = (fact["gross_amount"] * fact["discount_pct"] / 100).round(2)
    fact["net_amount"] = (fact["gross_amount"] - fact["discount_amount"]).round(2)

    order_total = fact.groupby("order_id")["net_amount"].transform("sum")
    fact["order_value_tier"] = np.select([order_total >= 500, order_total >= 100], ["HIGH", "MEDIUM"], "LOW")

    return fact[FACT_COLUMNS]
