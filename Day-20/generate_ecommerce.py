"""E-commerce data: customers -> products -> orders -> order_items"""
import random
from datetime import date, timedelta
from faker import Faker
from config import write_csv

random.seed(42)
Faker.seed(42)
fake = Faker("en_IN")          # Indian names, cities, phone numbers
DB = "ecommerce_db"
TODAY = date(2026, 11, 1)
N_CUSTOMERS, N_PRODUCTS, N_ORDERS = 5000, 500, 100000


def rand_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))


# Customers
customers = []
for cid in range(1, N_CUSTOMERS + 1):
    first, last = fake.first_name(), fake.last_name()
    customers.append([cid, first, last, f"{first}.{last}{cid}@example.com".lower(),
                      fake.phone_number(), fake.city(), fake.state(), "India",
                      rand_date(TODAY - timedelta(days=3 * 365), TODAY - timedelta(days=30))])
write_csv(DB, "customers", ["customer_id", "first_name", "last_name", "email", "phone",
                            "city", "state", "country", "created_at"], customers)

# Products
categories = {
    "Electronics": (["Phone", "Headphones", "Speaker", "Charger"], 500, 60000),
    "Clothing": (["T-Shirt", "Jeans", "Jacket", "Kurta"], 300, 5000),
    "Home": (["Lamp", "Cushion", "Kettle", "Mixer"], 200, 8000),
    "Books": (["Novel", "Guide", "Workbook"], 100, 1500),
    "Sports": (["Ball", "Racket", "Yoga Mat"], 200, 6000),
}
products = []
for pid in range(1, N_PRODUCTS + 1):
    cat = random.choice(list(categories))
    items, low, high = categories[cat]
    products.append([pid, f"{fake.word().title()} {random.choice(items)}", cat,
                     round(random.uniform(low, high), 2), random.randint(0, 500)])
write_csv(DB, "products", ["product_id", "name", "category", "price", "stock"], products)
price_of = {p[0]: p[3] for p in products}

# Orders + items. Some customers order much more than others (Pareto pattern).
weights = [random.paretovariate(1.5) for _ in customers]
orders, items = [], []
item_id = 1
for oid in range(1, N_ORDERS + 1):
    cust = random.choices(customers, weights)[0]
    order_date = rand_date(cust[8], TODAY)                 # never before signup
    if (TODAY - order_date).days <= 7:
        status = random.choice(["pending", "shipped"])
    else:
        status = random.choices(["delivered", "cancelled", "returned"], [85, 8, 7])[0]
    total = 0
    for pid in random.sample(range(1, N_PRODUCTS + 1), random.randint(1, 4)):
        qty = random.choices([1, 2, 3], [70, 20, 10])[0]
        total += qty * price_of[pid]
        items.append([item_id, oid, pid, qty, price_of[pid]])
        item_id += 1
    orders.append([oid, cust[0], order_date, status, round(total, 2)])

write_csv(DB, "orders", ["order_id", "customer_id", "order_date", "status", "total_amount"], orders)
write_csv(DB, "order_items", ["item_id", "order_id", "product_id", "quantity", "unit_price"], items)
