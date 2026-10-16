"""Project 5: Multi-level aggregations."""
import pandas as pd

df = pd.read_csv("data/clean_sales.csv", parse_dates=["order_date"])
df["month"] = df["order_date"].dt.to_period("M").astype(str)

# Group by 3 levels -> MultiIndex result
result = df.groupby(["region", "product", "month"])["revenue"].sum()
print("3-level groupby (first 8 rows):\n", result.head(8), "\n")

# Pick a level
print("Revenue per region (level 0):\n", result.groupby(level=0).sum(), "\n")

# Unstack: move the last level into columns
print("Revenue by region x product (unstack):\n", result.groupby(level=["region", "product"]).sum().unstack("product").fillna(0), "\n")

# Multi-level with several functions
summary = df.groupby(["region", "product"]).agg(
    orders=("order_id", "count"),
    revenue=("revenue", "sum"),
    avg_order=("revenue", "mean"),
).round(0)
print("Summary:\n", summary.head(10), "\n")

# Top product in each region
top = summary.reset_index().sort_values("revenue", ascending=False).groupby("region").head(1)
print("Best product per region:\n", top.sort_values("region"))
