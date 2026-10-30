import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

np.random.seed(42)
random.seed(42)

# -----------------------------
# CONFIG
# -----------------------------

NUM_CUSTOMERS = 2000
NUM_PRODUCTS = 300
NUM_STORES = 25
NUM_EMPLOYEES = 100
NUM_SALES = 50000

# -----------------------------
# REGIONS
# -----------------------------

regions = pd.DataFrame({
    "region_id": [1, 2, 3, 4],
    "region_name": ["North", "South", "East", "West"]
})

regions.to_csv("regions.csv", index=False)

# -----------------------------
# STORES
# -----------------------------

states = [
    "California", "Texas", "Florida", "New York",
    "Illinois", "CA", "TX", "FL", "NY"
]

stores = []

for i in range(1, NUM_STORES + 1):
    stores.append({
        "store_id": i,
        "store_name": f"Store_{i}",
        "city": fake.city(),
        "state": random.choice(states),
        "region_id": random.randint(1, 4),
        "manager_id": random.randint(1, NUM_EMPLOYEES)
    })

stores_df = pd.DataFrame(stores)

stores_df.to_csv("stores.csv", index=False)

# -----------------------------
# EMPLOYEES
# -----------------------------

employees = []

for i in range(1, NUM_EMPLOYEES + 1):
    employees.append({
        "employee_id": i,
        "employee_name": fake.name(),
        "department": random.choice([
            "Sales", "sales", "HR", "Finance",
            "Operations", "IT "
        ]),
        "salary": random.randint(40000, 120000)
    })

employees_df = pd.DataFrame(employees)

employees_df.to_csv("employees.csv", index=False)

# -----------------------------
# PRODUCTS
# -----------------------------

categories = [
    "Electronics", "electronics",
    "Furniture", "Office Supplies",
    "office supplies"
]

products = []

for i in range(1, NUM_PRODUCTS + 1):
    products.append({
        "product_id": i,
        "Product Name ": fake.word().title(),
        "category": random.choice(categories),
        "price": round(random.uniform(10, 1000), 2),
        "cost": round(random.uniform(5, 700), 2)
    })

products_df = pd.DataFrame(products)

products_df.to_csv("products.csv", index=False)

# -----------------------------
# CUSTOMERS
# -----------------------------

customers = []

for i in range(1, NUM_CUSTOMERS + 1):
    customers.append({
        "customer_id": i,
        "customer_name": fake.name() + " ",
        "email": fake.email(),
        "country": random.choice([
            "USA", "usa", "United States"
        ]),
        "age": random.randint(18, 70)
    })

customers_df = pd.DataFrame(customers)

customers_df.to_csv("customers.csv", index=False)

# -----------------------------
# SALES
# -----------------------------

sales = []

start_date = datetime(2023, 1, 1)

for i in range(1, NUM_SALES + 1):

    quantity = random.randint(1, 10)

    price = round(random.uniform(20, 1200), 2)

    discount = round(random.uniform(-0.1, 0.3), 2)

    sales.append({
        "order_id": i,
        "customer_id": random.randint(1, NUM_CUSTOMERS),
        "product_id": random.randint(1, NUM_PRODUCTS),
        "store_id": random.randint(1, NUM_STORES),
        "quantity": quantity,
        "unit_price": price,
        "discount": discount,
        "sales_amount": round(quantity * price * (1 - discount), 2),
        "order_status": random.choice([
            "Completed",
            "completed",
            "Pending",
            "Cancelled",
            "cancelled"
        ]),
        "order_date": start_date + timedelta(days=random.randint(0, 730)),
        "extra_column": "REMOVE_ME"
    })

sales_df = pd.DataFrame(sales)

# null quantities
for i in random.sample(range(NUM_SALES), 100):
    sales_df.loc[i, "quantity"] = None

sales_df.to_csv("sales.csv", index=False)

# -----------------------------
# CALENDAR
# -----------------------------

dates = pd.date_range(start="2023-01-01", end="2025-12-31")

calendar = pd.DataFrame({
    "date": dates,
    "year": dates.year,
    "month": dates.month,
    "month_name": dates.strftime("%B"),
    "quarter": dates.quarter
})

calendar.to_csv("calendar.csv", index=False)

print("All CSV files generated successfully!")