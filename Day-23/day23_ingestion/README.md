# Day 23 - Data Ingestion (Airflow + Docker + Snowflake)

Sources -> `data/staging/<source>/*.json` (raw NDJSON) -> Snowflake `RAW_<SOURCE>` tables (one VARIANT column).

| Source | Task | Snowflake table |
|---|---|---|
| JSONPlaceholder API (no auth) | api_posts | RAW_API_POSTS |
| GitHub API (bearer token) | api_github | RAW_API_GITHUB |
| CoinGecko API (API-key header) | api_crypto | RAW_API_CRYPTO |
| books.toscrape.com (static HTML) | scrape_books | RAW_SCRAPE_BOOKS |
| quotes.toscrape.com (dynamic JS) | scrape_quotes | RAW_SCRAPE_QUOTES |
| CSV / Excel / JSON in data/input | files | RAW_FILE_<FILENAME> |
| Source DB (incremental on updated_at) | db_orders | RAW_DB_ORDERS |

## Run
1. `cp .env.example .env` and fill in your Snowflake details
2. Run `sql/setup.sql` in Snowflake
3. `docker compose up --build -d`
4. `docker compose exec airflow python scripts/make_samples.py`  (sample files + source DB)
5. Open http://localhost:8080 - user `admin`, password: `docker compose exec airflow cat standalone_admin_password.txt`
6. Unpause + trigger `day23_ingestion`
7. Check: `SELECT COUNT(*) FROM RAW_DB_ORDERS;`

**Test incremental load:** `docker compose exec airflow python scripts/make_samples.py update`, trigger again.
Only the 10 changed/new orders are loaded.

Linux note: if `data/` isn't writable from the container, run `chmod -R 777 data`.
