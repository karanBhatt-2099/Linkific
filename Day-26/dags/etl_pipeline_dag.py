
import csv
import logging
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

log = logging.getLogger(__name__)

DATA = Path("/opt/airflow/data")
DB = DATA / "warehouse.db"
MAX_BAD_RATIO = 0.2  # fail quality check if >20% of rows are bad


# ---------------------------------------------------------------- monitoring
def send_alert(message):
    """Alert = log line + alerts.log file. Swap for email/Slack in real life."""
    log.error(message)
    with open(DATA / "alerts.log", "a") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} {message}\n")


def on_failure(context):
    """Failure callback: runs when a task fails after all retries."""
    ti = context["task_instance"]
    send_alert(f"TASK FAILED: {ti.dag_id}.{ti.task_id} run={context['run_id']} "
               f"error={context.get('exception')}")


def on_success(context):
    """Performance monitoring: log how long each task took."""
    ti = context["task_instance"]
    seconds = (datetime.now(timezone.utc) - ti.start_date).total_seconds()
    log.info("PERF: %s finished in %.2fs", ti.task_id, seconds)


# ------------------------------------------------------------------- extract
def extract_sales(ds):
    rows = [(i, i % 5 + 1, 10.0 * i) for i in range(1, 21)]
    rows[6] = (7, 3, -50.0)    # bad row: negative amount
    rows[12] = (13, None, 130.0)  # bad row: missing customer
    with open(DATA / f"raw_sales_{ds}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["order_id", "customer_id", "amount"])
        w.writerows(rows)
    log.info("Extracted %d sales rows", len(rows))


def extract_customers(ds):
    rows = [(i, f"  customer {i} ") for i in range(1, 6)]
    with open(DATA / f"raw_customers_{ds}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["customer_id", "name"])
        w.writerows(rows)
    log.info("Extracted %d customers", len(rows))


# ----------------------------------------------------------------- transform
def transform_sales(ds):
    good, bad = [], []
    with open(DATA / f"raw_sales_{ds}.csv") as f:
        for row in csv.DictReader(f):
            if row["customer_id"] and float(row["amount"]) > 0:
                good.append(row)
            else:
                bad.append(row)  # dead letter: keep bad rows, don't lose them
    _write(DATA / f"clean_sales_{ds}.csv", good, ["order_id", "customer_id", "amount"])
    _write(DATA / f"dead_letter_{ds}.csv", bad, ["order_id", "customer_id", "amount"])
    log.info("Sales: %d good, %d sent to dead letter", len(good), len(bad))


def transform_customers(ds):
    with open(DATA / f"raw_customers_{ds}.csv") as f:
        rows = [{"customer_id": r["customer_id"], "name": r["name"].strip().title()}
                for r in csv.DictReader(f)]
    _write(DATA / f"clean_customers_{ds}.csv", rows, ["customer_id", "name"])


def _write(path, rows, fields):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


# ---------------------------------------------------------------------- load
def load_sales(ds):
    with open(DATA / f"clean_sales_{ds}.csv") as f:
        rows = [(ds, r["order_id"], r["customer_id"], r["amount"]) for r in csv.DictReader(f)]
    with sqlite3.connect(DB) as db:
        db.execute("CREATE TABLE IF NOT EXISTS sales (ds TEXT, order_id INT, customer_id INT, amount REAL)")
        db.execute("DELETE FROM sales WHERE ds = ?", (ds,))  # re-runs stay safe
        db.executemany("INSERT INTO sales VALUES (?,?,?,?)", rows)
    log.info("Loaded %d sales rows", len(rows))


def load_customers(ds):
    with open(DATA / f"clean_customers_{ds}.csv") as f:
        rows = [(r["customer_id"], r["name"]) for r in csv.DictReader(f)]
    with sqlite3.connect(DB) as db:
        db.execute("CREATE TABLE IF NOT EXISTS customers (customer_id INT PRIMARY KEY, name TEXT)")
        db.executemany("INSERT OR REPLACE INTO customers VALUES (?,?)", rows)
    log.info("Loaded %d customers", len(rows))


# ------------------------------------------------------------- quality check
def quality_check(ds):
    with sqlite3.connect(DB) as db:
        loaded = db.execute("SELECT COUNT(*) FROM sales WHERE ds = ?", (ds,)).fetchone()[0]
    with open(DATA / f"dead_letter_{ds}.csv") as f:
        bad = len(list(csv.DictReader(f)))

    problems = []
    if loaded == 0:
        problems.append("no sales rows loaded")
    if loaded + bad and bad / (loaded + bad) > MAX_BAD_RATIO:
        problems.append(f"too many bad rows: {bad} of {loaded + bad}")

    if problems:
        send_alert(f"DATA QUALITY: {'; '.join(problems)} (ds={ds})")
        raise ValueError("; ".join(problems))
    log.info("Quality OK: %d loaded, %d in dead letter", loaded, bad)


# ----------------------------------------------------------------------- DAG
default_args = {
    "owner": "data-team",
    "retries": 2,                          # retry twice
    "retry_delay": timedelta(minutes=1),
    "retry_exponential_backoff": True,     # 1m, 2m, ...
    "execution_timeout": timedelta(minutes=5),
    "on_failure_callback": on_failure,
    "on_success_callback": on_success,
}

with DAG(
    dag_id="day26_etl_pipeline",
    description="Extract -> Transform -> Load -> Quality check",
    doc_md=__doc__,
    default_args=default_args,
    schedule="0 6 * * *",          # every day at 06:00
    start_date=datetime(2026, 11, 1),
    catchup=False,
    max_active_runs=1,             # one run at a time
    max_active_tasks=4,            # resource cap
    tags=["day26", "etl"],
) as dag:

    def task(task_id, func, doc):
        return PythonOperator(task_id=task_id, python_callable=func, doc_md=doc)

    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    t_extract_sales = task("extract_sales", extract_sales, "Create raw sales CSV (includes 2 bad rows).")
    t_extract_cust = task("extract_customers", extract_customers, "Create raw customers CSV.")
    t_transform_sales = task("transform_sales", transform_sales, "Drop bad rows into dead_letter CSV, keep clean rows.")
    t_transform_cust = task("transform_customers", transform_customers, "Trim and title-case names.")
    t_load_sales = task("load_sales", load_sales, "Load clean sales into SQLite (idempotent per date).")
    t_load_cust = task("load_customers", load_customers, "Upsert customers into SQLite.")
    t_quality = task("quality_check", quality_check, "Fail + alert if no rows loaded or too many bad rows.")

    # Dependencies: sales and customers branches run in parallel
    start >> [t_extract_sales, t_extract_cust]
    t_extract_sales >> t_transform_sales >> t_load_sales
    t_extract_cust >> t_transform_cust >> t_load_cust
    [t_load_sales, t_load_cust] >> t_quality >> end
