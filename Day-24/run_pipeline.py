"""Day-24 Data Warehouse pipeline for Snowflake. Credentials come from .env
Usage:
  python run_pipeline.py              # full build: schema, staging, dims, facts, validation
  python run_pipeline.py --scd-demo   # then change source customers, reload dims, show SCD2 history
"""
import argparse, os, sys, uuid
from pathlib import Path
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()
SQL = Path(__file__).parent / "sql"
REQ = ["SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD"]
missing = [k for k in REQ if not os.getenv(k)]
if missing:
    sys.exit(f"Missing in .env: {', '.join(missing)}")

DB = os.getenv("SNOWFLAKE_DATABASE", "DW_DAY24")
WH = os.getenv("SNOWFLAKE_WAREHOUSE", "DAY24_WH")
REPL = {"DB": DB, "WAREHOUSE": WH, "RUN_ID": str(uuid.uuid4())}

conn = snowflake.connector.connect(
    account=os.environ["SNOWFLAKE_ACCOUNT"], user=os.environ["SNOWFLAKE_USER"],
    password=os.environ["SNOWFLAKE_PASSWORD"], role=os.getenv("SNOWFLAKE_ROLE") or None)

def run(fname):
    sql = (SQL / fname).read_text()
    for k, v in REPL.items():
        sql = sql.replace("{{" + k + "}}", v)
    print(f"-> {fname}")
    cur = conn.execute_string(sql)[-1]
    return cur

def show(cur):
    cols = [c[0] for c in cur.description]
    rows = cur.fetchall()
    print(" | ".join(cols))
    for r in rows:
        print(" | ".join(str(x) for x in r))
    return rows, cols

ap = argparse.ArgumentParser()
ap.add_argument("--scd-demo", action="store_true")
args = ap.parse_args()

c = conn.cursor()
c.execute(f"CREATE WAREHOUSE IF NOT EXISTS {WH} WAREHOUSE_SIZE=XSMALL AUTO_SUSPEND=60 AUTO_RESUME=TRUE INITIALLY_SUSPENDED=TRUE")
c.execute(f"USE WAREHOUSE {WH}")

if not args.scd_demo:
    for f in ["01_schema.sql", "02_staging_sample_data.sql", "03_dim_date.sql",
              "04_load_dimensions.sql", "05_load_facts.sql"]:
        run(f)
else:
    run("07_scd2_demo.sql"); run("04_load_dimensions.sql")
    print("\nSCD2 history:"); show(run("08_demo_query.sql"))

print("\nValidation results:")
rows, cols = show(run("06_validation.sql"))
status_idx = cols.index("STATUS")
fails = [r for r in rows if r[status_idx] == "FAIL"]
conn.close()
print(f"\n{len(rows)} checks | {sum(r[status_idx]=='PASS' for r in rows)} PASS | "
      f"{sum(r[status_idx]=='WARN' for r in rows)} WARN | {len(fails)} FAIL")
sys.exit(1 if fails else 0)