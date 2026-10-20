"""Step 1: Combining DataFrames - merge, join, concat."""
import pandas as pd

customers = pd.read_csv("data/customers.csv")
products = pd.read_csv("data/products.csv")
orders = pd.read_csv("data/orders.csv", parse_dates=["order_date"])

print("Orders:", orders.shape, "| Customers:", customers.shape, "| Products:", products.shape)

# 1. MERGE (SQL-like joins) - orders + customers on customer_id

inner = orders.merge(customers, on="customer_id", how="inner")   # only matching rows
left = orders.merge(customers, on="customer_id", how="left")     # all orders
right = orders.merge(customers, on="customer_id", how="right")   # all customers
outer = orders.merge(customers, on="customer_id", how="outer")   # everything

print("\n--- Join types (rows) ---")
print("inner:", len(inner), "| left:", len(left), "| right:", len(right), "| outer:", len(outer))

# Orders whose customer does not exist -> region is NaN after a left join
print("Orders with unknown customer:", left["region"].isna().sum())

# 2. indicator=True shows where each row came from

check = orders.merge(customers, on="customer_id", how="outer", indicator=True)
print("\n--- Merge indicator ---")
print(check["_merge"].value_counts())


# 3. Different key names: left_on / right_on
cust_renamed = customers.rename(columns={"customer_id": "cust_id"})
diff_keys = orders.merge(cust_renamed, left_on="customer_id", right_on="cust_id")
print("\nDifferent key names ->", diff_keys.shape)


# 4. Multi-table merge (orders + customers + products)
full = (
    orders
    .merge(customers, on="customer_id", how="inner")
    .merge(products, on="product_id", how="inner")
)
full["revenue"] = full["quantity"] * full["price"]
print("\n--- Full dataset (3 tables) ---")
print(full.head())
full.to_csv("output/full_sales.csv", index=False)


# 5. Multi-key merge: join on TWO columns (region + month)
full["month"] = full["order_date"].dt.to_period("M").astype(str)
monthly = full.groupby(["region", "month"], as_index=False)["revenue"].sum()

targets = monthly[["region", "month"]].copy()
targets["target"] = 5000          # pretend every region has a 5000 monthly target

multi = monthly.merge(targets, on=["region", "month"])
multi["achieved_%"] = (multi["revenue"] / multi["target"] * 100).round(1)
print("\n--- Multi-key merge ---")
print(multi.head())

# ------------------------------------------------------------
# 6. Same column name in both tables -> suffixes
# ------------------------------------------------------------
a = pd.DataFrame({"id": [1, 2], "value": [10, 20]})
b = pd.DataFrame({"id": [1, 2], "value": [100, 200]})
print("\n--- suffixes ---")
print(a.merge(b, on="id", suffixes=("_old", "_new")))


# 7. validate: catch duplicate keys early
try:
    orders.merge(customers, on="customer_id", validate="one_to_one")
except Exception as e:
    print("\nvalidate caught a problem:", type(e).__name__)

# 8. JOIN (merge on the index)
cust_idx = customers.set_index("customer_id")
joined = orders.join(cust_idx, on="customer_id", how="left")
print("\n--- join on index ---", joined.shape)

# 9. CONCAT
# Stack rows (append): 2024 orders + 2025 orders
o2024 = orders[orders["order_date"].dt.year == 2024]
o2025 = orders[orders["order_date"].dt.year == 2025]
stacked = pd.concat([o2024, o2025], ignore_index=True)
print("\nconcat rows:", len(o2024), "+", len(o2025), "=", len(stacked))

# Side by side (columns)
side = pd.concat([customers[["customer_id"]], customers[["region"]]], axis=1)
print("concat columns:", side.shape)
