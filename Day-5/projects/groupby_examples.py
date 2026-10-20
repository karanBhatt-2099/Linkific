"""Groupby and aggregation examples on the clean sales data (run project1 first)."""
import pandas as pd

df = pd.read_csv("data/clean_sales.csv", parse_dates=["order_date"])

print("1. Total revenue by region:\n", df.groupby("region")["revenue"].sum(), "\n")

print("2. Several stats per product:\n",
      df.groupby("product")["revenue"].agg(["count", "sum", "mean"]).round(0), "\n")

print("3. Named aggregations:\n",
      df.groupby("region").agg(orders=("order_id", "count"),
                               units=("quantity", "sum"),
                               revenue=("revenue", "sum")), "\n")

print("4. Pivot table (product x region):\n",
      pd.pivot_table(df, values="revenue", index="product", columns="region",
                     aggfunc="sum", fill_value=0), "\n")

print("5. Crosstab (product x region counts):\n", pd.crosstab(df["product"], df["region"]), "\n")

df["pct_of_region"] = (df["revenue"] / df.groupby("region")["revenue"].transform("sum") * 100).round(1)
print("6. Transform - % of region revenue per order:\n", df[["region", "revenue", "pct_of_region"]].head(), "\n")

busy = df.groupby("customer_name").filter(lambda g: len(g) >= 12)
print("7. Filter - customers with 12+ orders:", busy["customer_name"].unique())
