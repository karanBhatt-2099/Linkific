# Transactions: commit when OK, rollback when something fails
import sys; sys.path.append("..")
import psycopg2
from config import PG

conn = psycopg2.connect(**PG)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        id SERIAL PRIMARY KEY, name TEXT, balance INT
    )
""")
cur.execute("DELETE FROM accounts")
cur.execute("INSERT INTO accounts (name, balance) VALUES ('A', 1000), ('B', 500)")
conn.commit()

try:
    # Transfer 200 from A to B (both steps must succeed together)
    cur.execute("UPDATE accounts SET balance = balance - 200 WHERE name = 'A'")
    cur.execute("UPDATE accounts SET balance = balance + 200 WHERE name = 'B'")
    conn.commit()
    print("Transfer done (committed)")
except Exception as e:
    conn.rollback()
    print("Error, rolled back:", e)

cur.execute("SELECT * FROM accounts ORDER BY id")
print(cur.fetchall())

cur.close()
conn.close()
