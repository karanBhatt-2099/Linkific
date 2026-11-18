"""Creates a small sales data warehouse (star schema) in SQLite: data/warehouse.db"""
import sqlite3
import numpy as np
import pandas as pd

np.random.seed(42)

# ---------- dim_date ----------
dates = pd.date_range("2023-01-01", "2024-12-31")
dim_date = pd.DataFrame({
    "date_key": dates.strftime("%Y%m%d").astype(int),
    "full_date": dates.strftime("%Y-%m-%d"),
    "year": dates.year,
    "quarter": dates.quarter,
    "month": dates.month,
    "month_name": dates.strftime("%b"),
    "day_name": dates.strftime("%a"),
    "is_weekend": (dates.dayofweek >= 5).astype(int),
})

# ---------- dim_customer ----------
n_cust = 500
dim_customer = pd.DataFrame({
    "customer_key": range(1, n_cust + 1),
    "customer_name": [f"Customer {i}" for i in range(1, n_cust + 1)],
    "segment": np.random.choice(["Consumer", "Corporate", "Small Business"], n_cust, p=[0.5, 0.3, 0.2]),
    "region": np.random.choice(["North", "South", "East", "West"], n_cust),
})

# ---------- dim_product ----------
categories = {"Electronics": (200, 900), "Furniture": (100, 600),
              "Office Supplies": (5, 80), "Clothing": (20, 150)}
rows, key = [], 1
for cat, (lo, hi) in categories.items():
    for i in range(10):
        price = round(np.random.uniform(lo, hi), 2)
        rows.append((key, f"{cat} Item {i+1}", cat, price, round(price * np.random.uniform(0.5, 0.8), 2)))
        key += 1
dim_product = pd.DataFrame(rows, columns=["product_key", "product_name", "category", "unit_price", "unit_cost"])

# ---------- fact_sales ----------
n = 20000
f = pd.DataFrame({
    "date_key": np.random.choice(dim_date["date_key"], n),
    "customer_key": np.random.choice(dim_customer["customer_key"], n),
    "product_key": np.random.choice(dim_product["product_key"], n),
    "quantity": np.random.randint(1, 6, n),
})
# Seasonality: extra sales in Nov/Dec. Growth: extra sales in 2024.
month = (f["date_key"] // 100) % 100
holiday = f[month >= 11].sample(frac=0.5, random_state=1)
growth = f[f["date_key"] >= 20240101].sample(frac=0.25, random_state=2)
f = pd.concat([f, holiday, growth], ignore_index=True)
f.insert(0, "sale_id", range(1, len(f) + 1))
f = f.merge(dim_product[["product_key", "unit_price", "unit_cost"]], on="product_key")
f["discount"] = np.random.choice([0, 0.05, 0.10, 0.20], len(f), p=[0.6, 0.2, 0.15, 0.05])
f["revenue"] = (f["quantity"] * f["unit_price"] * (1 - f["discount"])).round(2)
f["cost"] = (f["quantity"] * f["unit_cost"]).round(2)
fact_sales = f[["sale_id", "date_key", "customer_key", "product_key", "quantity", "discount", "revenue", "cost"]]

con = sqlite3.connect("data/warehouse.db")
for name, df in [("dim_date", dim_date), ("dim_customer", dim_customer),
                 ("dim_product", dim_product), ("fact_sales", fact_sales)]:
    df.to_sql(name, con, if_exists="replace", index=False)
    df.to_csv(f"data/{name}.csv", index=False)   # CSVs can be imported into Power BI
con.close()
print("Done. fact_sales rows:", len(fact_sales))
