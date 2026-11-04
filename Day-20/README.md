# Day 20 – Synthetic Data Generation (Faker + PostgreSQL)

Generates realistic fake data with the **Faker** library, keeps table relationships
consistent, and bulk-loads it into **PostgreSQL** (viewed with **pgAdmin**).

## Folder structure
```
day20_synthetic_data/
├── 01_faker_basics.py        # Faker demo: providers, dates, company/internet, localization
├── generate_ecommerce.py     # customers, products, orders, order_items
├── generate_hr.py            # departments, employees, attendance
├── generate_finance.py       # accounts, transactions
├── generate_all.py           # runs all three generators -> CSV files
├── load_to_db.py             # create DBs, bulk insert (COPY), indexes
├── validate.py               # row counts + relationship checks
├── test_connection.py        # checks your .env connection works
├── config.py                 # reads settings from .env
├── .env                      # YOUR DB host / port / user / password (edit this)
├── .env.example              # template copy of .env
├── requirements.txt
├── sql/                      # *_schema.sql, *_indexes.sql, sample_queries.sql
└── data/                     # generated CSV files (ready to load)
```

## How to run
1. Install PostgreSQL + pgAdmin and make sure the server is running.
2. Open the `.env` file and set `DB_PASSWORD` (and user/host/port if different):
```
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_pgadmin_password
```
   Use the same details you use to log in to the server in pgAdmin
   (pgAdmin → right-click your server → Properties → Connection shows host, port, username).
3. Run:
```bash
pip install -r requirements.txt
python test_connection.py      # should print "Connected!"
python 01_faker_basics.py      # optional: Faker demo
python generate_all.py         # optional: CSVs are already in data/
python load_to_db.py           # create 3 databases and load them
python validate.py             # check everything is consistent
```
4. In pgAdmin: right-click **Databases → Refresh**. You will see `ecommerce_db`,
   `hr_db` and `finance_db`. Try `sql/sample_queries.sql` in the Query Tool.

## Troubleshooting
- **password authentication failed** – wrong `DB_PASSWORD` in `.env`.
- **connection refused** – PostgreSQL service is not running, or the port is not 5432.
- **database is being accessed by other users** – disconnect the database in pgAdmin, then rerun `load_to_db.py`.

## The 3 databases
| Database | Tables (rows) |
|---|---|
| `ecommerce_db` | customers (5,000), products (500), **orders (100,000)**, order_items (~250,000) |
| `hr_db` | departments (10), employees (1,000), **attendance (~128,000)** |
| `finance_db` | accounts (2,000), **transactions (~150,000)** |

Total: ~640,000 rows. Every table with 100k+ rows is in bold.

## How relationships are maintained
- **Foreign keys** – parents are generated and loaded first (customers → orders → order_items).
- **Date ranges** – orders are never before the customer signed up; attendance is never before
  the hire date; transactions are never before the account opened date.
- **Logical constraints** – order total = sum of its items; a withdrawal is never larger than the
  balance (so no negative balance); account balance = last transaction's `balance_after`;
  employees report to their department head.
- **Distribution patterns** – a few customers place many orders (Pareto), order status
  follows weights (85% delivered, 8% cancelled, 7% returned), attendance is ~85% present,
  amounts use a log-normal curve (many small, few large).
- **Localization** – names, cities and phone numbers use `Faker("en_IN")`.
- **Reproducible** – fixed random seeds, so you get the same data every run.

## Load strategy for large data
1. Create tables **without** indexes.
2. Bulk load with `COPY` (far faster than row-by-row `INSERT`).
3. Create indexes **after** loading, then `ANALYZE`.
4. Run `validate.py` – all checks should show `PASS`.

## Change the size
Edit the constants at the top of each generator, e.g. `N_ORDERS = 100000` in
`generate_ecommerce.py`, then run `generate_all.py` and `load_to_db.py` again.
