# Day 10 – Python + Databases

Connect Python to PostgreSQL, run SQL, use SQLAlchemy, build a simple ETL pipeline.

## Setup
```bash
pip install -r requirements.txt
# create the database once (in psql):  CREATE DATABASE day10_db;
```
Edit `config.py` (host, user, password) or set env variables like `PG_PASSWORD`.

## Folder Guide
| Folder | What's inside |
|---|---|
| `1_psycopg2/` | Connect, insert, fetch, parameterized queries, commit/rollback |
| `2_pandas_sql/` | `to_sql`, `read_sql_query`, `read_sql_table`, chunks |
| `3_sqlalchemy_orm/` | Model class + CRUD + queries |
| `4_pipelines/` | CSV → PostgreSQL and API → PostgreSQL (incremental) |
| `5_practice/` | DB → pandas analysis, multi-database merge |
| `data/` | Sample `employees.csv` |

## Run Order
Run scripts from inside their own folder (they use `../config.py`):
```bash
cd 1_psycopg2        && python 01_connect_and_query.py && python 02_transactions.py
cd ../2_pandas_sql   && python pandas_sql_demo.py          # creates 'employees' table
cd ../3_sqlalchemy_orm && python crud_demo.py
cd ../4_pipelines    && python csv_to_postgres.py && python api_to_db_pipeline.py
cd ../5_practice     && python db_to_pandas_analysis.py && python multi_database_queries.py
```
Run `2_pandas_sql` before `5_practice` (it needs the `employees` table).

## Integration Patterns

**1. Raw SQL (psycopg2)** – full control, good for small scripts.
```python
cur.execute("SELECT * FROM t WHERE x > %s", (5,))   # always use %s params
```

**2. pandas + SQL** – best for analysis.
```python
df = pd.read_sql_query("SELECT * FROM t", engine)
df.to_sql("t2", engine, if_exists="replace", index=False)
```
`chunksize=N` reads big tables in pieces.

**3. SQLAlchemy ORM** – tables as Python classes.
```python
session.add(Employee(name="Asha")); session.commit()
session.query(Employee).filter(Employee.salary > 5).all()
```

**4. ETL pipeline** – three small functions: `extract()` → `transform()` → `load()`.

**5. Incremental loading** – read existing ids, insert only new ones.

**6. Error handling** – `try/except` around the pipeline, `timeout` + `raise_for_status()` on API calls, `rollback()` on DB errors.

## Quick Rules
- Never build SQL with f-strings from user input (SQL injection). Use parameters.
- Always `commit()` after INSERT/UPDATE/DELETE; `rollback()` on error.
- Close connections and sessions when done.
- Keep the DB URL in one place (`config.py`).

## Note
Scripts were tested with SQLite as a stand-in; swap in PostgreSQL via `config.py`. The API pipeline needs internet access.
