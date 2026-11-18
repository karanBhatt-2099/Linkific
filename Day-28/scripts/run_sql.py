"""Runs every .sql file against warehouse.db and prints results (quick check)."""
import sqlite3, glob
import pandas as pd

con = sqlite3.connect("data/warehouse.db")
for path in sorted(glob.glob("sql/*.sql")):
    print("\n" + "=" * 20, path, "=" * 20)
    for stmt in open(path).read().split(";"):
        if "SELECT" in stmt.upper():
            print(pd.read_sql(stmt, con).to_string(index=False), "\n")
