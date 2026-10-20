import numpy as np
import pandas as pd

np.random.seed(42)

# --- Customers ---
n_customers = 100
customers = pd.DataFrame({
    "customer_id": range(1, n_customers + 1),
    "customer_name": [f"Customer {i}" for i in range(1, n_customers + 1)],
    "region": np.random.choice(["North", "South", "East", "West"], n_customers),
})

# --- Products ---
products = pd.DataFrame({
    "product_id": range(1, 11),
    "product_name": [f"Product {c}" for c in "ABCDEFGHIJ"],
    "category": ["Tech", "Tech", "Tech", "Home", "Home", "Home", "Toys", "Toys", "Food", "Food"],
    "price": [250, 120, 80, 60, 45, 30, 25, 15, 10, 5],
})

# --- Orders (a few customer ids do NOT exist, so joins are interesting) ---
n_orders = 1000
orders = pd.DataFrame({
    "order_id": range(1, n_orders + 1),
    "order_date": pd.date_range("2024-01-01", "2025-12-31", periods=n_orders).normalize(),
    "customer_id": np.random.randint(1, n_customers + 6, n_orders),
    "product_id": np.random.randint(1, 11, n_orders),
    "quantity": np.random.randint(1, 6, n_orders),
})

# --- Save CSVs ---
customers.to_csv("data/customers.csv", index=False)
products.to_csv("data/products.csv", index=False)
orders.to_csv("data/orders.csv", index=False)

# --- Save the Excel input workbook (multiple sheets) ---
with pd.ExcelWriter("data/sales_data.xlsx") as writer:
    customers.to_excel(writer, sheet_name="Customers", index=False)
    products.to_excel(writer, sheet_name="Products", index=False)
    orders.to_excel(writer, sheet_name="Orders", index=False)

# --- Big CSV for the chunk-processing demo (500,000 rows) ---
big = pd.DataFrame({
    "id": range(500_000),
    "city": np.random.choice(["Mumbai", "Delhi", "Pune", "Chennai", "Kolkata"], 500_000),
    "amount": np.random.rand(500_000) * 1000,
    "qty": np.random.randint(1, 10, 500_000),
})
big.to_csv("data/big_file.csv", index=False)

print("Created: customers.csv, products.csv, orders.csv, sales_data.xlsx, big_file.csv")
