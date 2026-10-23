# psycopg2 basics: connect, execute, fetch, parameterized queries
import sys; sys.path.append("..")
import psycopg2
from config import PG

# 1. Connect
conn = psycopg2.connect(**PG)
cur = conn.cursor()
print("Connected!")

# 2. Create table
cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id SERIAL PRIMARY KEY,
        name TEXT,
        marks INT
    )
""")

# 3. Insert using parameters (%s) -- NEVER use f-strings in SQL
cur.execute("INSERT INTO students (name, marks) VALUES (%s, %s)", ("Asha", 90))
cur.executemany(
    "INSERT INTO students (name, marks) VALUES (%s, %s)",
    [("Ravi", 75), ("Neha", 82)],
)
conn.commit()

# 4. Fetch results
cur.execute("SELECT * FROM students")
print("All rows:", cur.fetchall())

cur.execute("SELECT * FROM students WHERE marks > %s", (80,))
print("Marks > 80:", cur.fetchall())

cur.execute("SELECT * FROM students LIMIT 1")
print("One row:", cur.fetchone())

# 5. Close
cur.close()
conn.close()
