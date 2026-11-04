"""Run this first to check your .env settings work with PostgreSQL / pgAdmin."""
import psycopg2
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD

try:
    conn = psycopg2.connect(dbname="postgres", user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    cur = conn.cursor()
    cur.execute("SELECT version()")
    print("Connected!", cur.fetchone()[0])
    conn.close()
except Exception as e:
    print("Connection failed:", e)
    print("Check DB_HOST, DB_PORT, DB_USER, DB_PASSWORD in the .env file.")
