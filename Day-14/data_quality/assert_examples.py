"""Simple assert-based validation (pandas, small data).
Run from the project root:  python data_quality/assert_examples.py"""
import pandas as pd

df = pd.read_csv("data/orders.csv")

checks = {
    "has rows":          lambda: len(df) > 0,
    "columns exist":     lambda: {"order_id", "price", "quantity"} <= set(df.columns),
    "order_id not null": lambda: df["order_id"].notnull().all(),
    "order_id unique":   lambda: df["order_id"].is_unique,
    "quantity > 0":      lambda: (df["quantity"] > 0).all(),
    "price not null":    lambda: df["price"].notnull().all(),
}

# We catch AssertionError so ALL checks run and print.
for name, check in checks.items():
    try:
        assert check(), name
        print("PASS:", name)
    except AssertionError:
        print("FAIL:", name)

# Plain style (stops the script immediately on failure):
# assert df["price"].notnull().all(), "Price has missing values!"
