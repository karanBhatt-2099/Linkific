"""Creates 3 small messy datasets for the practice projects."""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

# ---------- 1. Messy sales ----------
n = 60
sales = pd.DataFrame({
    "Order ID": range(1001, 1001 + n),
    " Customer Name ": rng.choice(["  alice ", "BOB", "Charlie", "dave  ", "Eve"], n),
    "Product": rng.choice(["Laptop", "Phone", "tablet", "PHONE", "Mouse"], n),
    "Quantity": rng.integers(1, 6, n).astype(object),
    "Price": rng.choice([999.0, 599.0, 399.0, 25.0], n).astype(object),
    "Order Date": pd.date_range("2024-01-01", periods=n, freq="3D").strftime("%Y-%m-%d").astype(object),
    "Region": rng.choice(["North", "South", "East", "West", None], n),
})
sales.loc[[3, 10, 25], "Quantity"] = None
sales.loc[[5, 30], "Price"] = "$599"
sales.loc[[8], "Order Date"] = "not a date"
sales = pd.concat([sales, sales.iloc[[2, 7]]], ignore_index=True)  # duplicates
sales.to_csv("data/messy_sales.csv", index=False)

# ---------- 2. Messy customers ----------
customers = pd.DataFrame({
    "cust_id": range(1, 41),
    "name": rng.choice(["Ann Lee", "raj patel", "MARIA GARCIA", " John Smith ", "Li Wei"], 40),
    "email": rng.choice(["a@x.com", "B@X.COM", None, "c@y.com", "d@z.com "], 40),
    "age": rng.choice([22, 35, 41, 29, None, 58, 67], 40),
    "city": rng.choice(["Mumbai", "mumbai ", "Delhi", "PUNE", "Pune", None], 40),
    "signup_date": pd.date_range("2023-01-01", periods=40, freq="9D").strftime("%d/%m/%Y"),
    "total_spent": rng.integers(100, 5000, 40),
})
customers = pd.concat([customers, customers.iloc[[1, 4, 9]]], ignore_index=True)
customers.to_csv("data/messy_customers.csv", index=False)

# ---------- 3. Messy employees (JSON-style text columns) ----------
emp = pd.DataFrame({
    "EmpID": range(1, 31),
    "Full Name": rng.choice(["sara khan", "AMIT SHAH", "Neha  Rao", "vikram Jain"], 30),
    "Department": rng.choice(["HR", "hr", "Tech", "TECH", "Finance", None], 30),
    "Salary": rng.choice(["50000", "62,000", "75000", "N/A", "88,500"], 30),
    "Join Date": pd.date_range("2020-01-15", periods=30, freq="45D").strftime("%d-%m-%Y"),
})
emp = pd.concat([emp, emp.iloc[[0, 5]]], ignore_index=True)
emp.to_csv("data/messy_employees.csv", index=False)

# ---------- Orders for merge examples ----------
pd.DataFrame({"customer_id": [1, 2, 3, 4], "name": ["Ann", "Raj", "Maria", "John"],
              "city": ["Mumbai", "Delhi", "Pune", "Goa"]}).to_csv("data/customers_small.csv", index=False)
pd.DataFrame({"order_id": [101, 102, 103, 104, 105], "customer_id": [1, 1, 2, 3, 9],
              "amount": [250, 400, 150, 300, 500]}).to_csv("data/orders_small.csv", index=False)
print("Data created in /data")
