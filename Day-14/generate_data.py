"""Creates a large orders.csv (with some deliberately bad rows) and a small customers.csv."""
import csv
import random
from datetime import date, timedelta

random.seed(42)
N = 500_000
products = {"Laptop": "Electronics", "Phone": "Electronics", "Shirt": "Clothing",
            "Shoes": "Clothing", "Book": "Books", "Pen": "Stationery"}
countries = ["India", "USA", "UK", "Germany"]

with open("data/orders.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["order_id", "customer_id", "product", "category",
                "quantity", "price", "order_date", "country"])
    for i in range(1, N + 1):
        product = random.choice(list(products))
        row = [i, random.randint(1, 1000), product, products[product],
               random.randint(1, 5), round(random.uniform(5, 1000), 2),
               date(2024, 1, 1) + timedelta(days=random.randint(0, 365)),
               random.choice(countries)]
        # inject bad data (~1% each)
        r = random.random()
        if r < 0.01:
            row[4] = -1            # negative quantity
        elif r < 0.02:
            row[5] = None          # missing price
        elif r < 0.03:
            row[7] = "Mars"        # invalid country
        elif r < 0.04:
            row[0] = random.randint(1, i)   # duplicate order_id
        w.writerow(row)

with open("data/customers.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["customer_id", "name", "city"])
    for c in range(1, 1001):
        w.writerow([c, f"Customer_{c}", random.choice(["Mumbai", "Delhi", "London", "Berlin", "NYC"])])

print("Created data/orders.csv and data/customers.csv")
