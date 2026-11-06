# Day 22 – E-commerce Analytics Platform

**Goal:** design a complete data platform – plan the architecture, define requirements, set up the infrastructure.

**Stack:** Snowflake (data warehouse) · Apache Airflow (Docker) · Python · Power BI (later days) · Great Expectations (later days)

---

## 1. Requirements

### 1.1 Data sources

| Source | What we get | How | Format |
|---|---|---|---|
| Fake Store API `/products` | product catalog (title, category, price, rating) | REST API | JSON |
| Fake Store API `/users` | customers (name, email, city) | REST API | JSON |
| Fake Store API `/carts` | orders with product lines + quantity + date | REST API | JSON |
| *(Phase 2)* Inventory feed | stock level per product | API / events | JSON |

API used: https://fakestoreapi.com (free, no key needed – good for learning).

### 1.2 Data volume

| | Demo (now) | Design target (what the schema should handle) |
|---|---|---|
| Products | ~20 | 10,000 |
| Customers | ~10 | 100,000 |
| Order lines / year | ~30 | 1,000,000 |
| Growth | – | ~20% per year |

Snowflake handles the target volume easily on an X-Small warehouse.

### 1.3 Update frequency

| Data | Frequency |
|---|---|
| Products, customers, orders | Daily batch (Airflow `@daily`) |
| Inventory (Phase 2) | Near real-time (every 5–15 min) |

### 1.4 Analytics needs

1. Total revenue, orders and units sold – by day / month / year
2. Top-selling products and categories
3. Revenue per customer, repeat vs new customers
4. Average order value (AOV)
5. Sales by city
6. Low-stock / out-of-stock products *(Phase 2)*

### 1.5 Dashboard requirements (Power BI)

- **Page 1 – Executive summary:** revenue, orders, AOV cards + monthly revenue trend
- **Page 2 – Products:** top 10 products, revenue by category
- **Page 3 – Customers:** top customers, sales by city
- **Page 4 – Inventory:** stock levels and alerts *(Phase 2)*
- Filters: date range, category, city
- Refresh: daily, after the Airflow run finishes
- Connects to Snowflake `ANALYTICS` schema only (never `RAW`)

### 1.6 User personas

| Persona | Needs | Uses |
|---|---|---|
| **Maya – Business Owner** | "How are sales this month?" – quick KPIs | Executive summary page |
| **Raj – Category Manager** | Which products/categories sell, what to restock | Products + Inventory pages |
| **Anita – Data Analyst** | Clean star schema to write her own SQL | Snowflake `ANALYTICS` tables |
| **Dev – Data Engineer (you)** | Reliable pipelines, easy monitoring | Airflow UI, Snowflake |

---

## 2. Architecture

```
 Fake Store API ──►  Airflow (Docker)  ──►  Snowflake                    ──►  Power BI
 (products,          extract (Python)       RAW        (as-is copy)          (dashboard)
  users, carts)      load raw               ANALYTICS  (star schema)
                     check quality (GE)
                     transform (SQL)
```

**Flow of one daily run (the DAG):**

```
extract_and_load_raw ──► data_quality_checks ──► build_dimensions ──► build_fact_sales
```

If `data_quality_checks` fails, the run stops and the star schema keeps yesterday's good data.

**Why this design**
- **RAW layer** keeps an untouched copy of source data – easy to re-run transforms.
- **ANALYTICS layer** is a star schema – fast and simple for BI tools.
- **SQL transforms inside Snowflake** (ELT) – less Python code, warehouse does the heavy work.
- **Full refresh each day** – simplest approach, fine at this data size. (Incremental loads can come later.)

### Star schema

```
                 dim_date
                    │
 dim_customer ── fact_sales ── dim_product
```

| Table | Grain / key | Main columns |
|---|---|---|
| `fact_sales` | one row per product in an order | cart_id, date_key, customer_key, product_key, quantity, unit_price, total_amount |
| `dim_product` | one row per product | product_key, title, category, price, rating |
| `dim_customer` | one row per customer | customer_key, full_name, email, city |
| `dim_date` | one row per day | date_key (YYYYMMDD), date, year, quarter, month, month_name, day_of_week |

---

## 3. Infrastructure setup

### Data quality checks (Great Expectations)

The `data_quality_checks` task reads the three RAW tables and validates them with Great Expectations (in-memory, no config files):

| Table | Checks |
|---|---|
| `RAW.PRODUCTS` | at least 1 row · `id` not null + unique · `title` not null · `price` > 0 · `rating_rate` between 0 and 5 |
| `RAW.USERS` | at least 1 row · `id` not null + unique · `email` not null |
| `RAW.CART_ITEMS` | at least 1 row · `cart_id`, `cart_date` not null · `quantity` > 0 · every `product_id` exists in products · every `user_id` exists in users |

Any failed check raises an error listing what failed, the task turns red in Airflow, and the transform tasks do not run. To add a check, add one line to the list in `data_quality_checks()` in the DAG file.

### Project layout

```
ecommerce-analytics-platform/
├── docker-compose.yml        # Airflow in Docker
├── Dockerfile                # Airflow + Snowflake connector + Great Expectations
├── requirements.txt
├── .env.example              # copy to .env and fill in
├── sql/01_snowflake_setup.sql  # warehouse, database, schemas, tables
└── dags/ecommerce_etl.py     # the pipeline
```

### Step 1 – Snowflake

1. Create a Snowflake account (free trial works).
2. In a Snowflake worksheet run `sql/01_snowflake_setup.sql`. It creates:
   warehouse `ECOM_WH`, database `ECOM_DB`, schemas `RAW` and `ANALYTICS`, and all tables.
3. Pick how Airflow will log in:
   - **Password** – simplest, put it in `.env`.
   - **Key pair** (recommended – Snowflake has been tightening password-only logins):
     ```bash
     openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt
     openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub
     ```
     Then in Snowflake: `ALTER USER <your_user> SET RSA_PUBLIC_KEY='<public key without header/footer lines>';`
     Move `rsa_key.p8` into a `keys/` folder in the project, set `SNOWFLAKE_PRIVATE_KEY_PATH=/opt/airflow/keys/rsa_key.p8` in `.env`, and leave `SNOWFLAKE_PASSWORD` empty.

### Step 2 – Environment variables

```bash
cp .env.example .env      # then edit .env with your Snowflake details
```

`SNOWFLAKE_ACCOUNT` looks like `orgname-accountname` (find it in Snowflake: *Account menu → View account details*).

### Step 3 – Start Airflow

```bash
docker compose up -d --build
docker compose logs -f airflow       # wait until you see "Airflow is ready"
```

- Open http://localhost:8080
- Username: `admin`
- Password: `docker compose exec airflow cat /opt/airflow/standalone_admin_password.txt`

### Step 4 – Run the pipeline

1. In the Airflow UI, un-pause the DAG **`ecommerce_etl`**.
2. Click **Trigger DAG**.
3. All 4 tasks should turn green. (Click `data_quality_checks` → Logs to see "All data quality checks passed".)
4. Check in Snowflake:
   ```sql
   SELECT * FROM ECOM_DB.ANALYTICS.FACT_SALES LIMIT 10;
   ```

### Stop / clean up

```bash
docker compose down        # stop and remove the container
```

(Airflow's own metadata is not persisted in this simple setup – a new admin password is generated after each `down`/`up`. Your data lives in Snowflake, so nothing is lost.)

---

## 4. Day-22 checklist

- [x] Project domain chosen: E-commerce Analytics
- [x] Data sources, volume, frequency defined
- [x] Analytics needs, dashboard requirements, personas defined
- [x] Architecture designed (RAW → star schema → dashboard)
- [x] Data quality checks added (Great Expectations)
- [ ] Snowflake objects created (`01_snowflake_setup.sql`)
- [ ] Airflow running in Docker
- [ ] First DAG run successful

## 5. Coming next

- Power BI dashboard on `ANALYTICS`
- Real-time inventory tracking (Phase 2)
