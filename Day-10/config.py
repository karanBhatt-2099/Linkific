# Change these to match your PostgreSQL setup (or set env variables)
import os

PG = {
    "host": os.getenv("PG_HOST", "localhost"),
    "port": os.getenv("PG_PORT", "5432"),
    "dbname": os.getenv("PG_DB", "day10_db"),
    "user": os.getenv("PG_USER", "postgres"),
    "password": os.getenv("PG_PASSWORD", "**********"),
}

# SQLAlchemy / pandas use one URL string
DB_URL = os.getenv(
    "DB_URL",
    f"postgresql://{PG['user']}:{PG['password']}@{PG['host']}:{PG['port']}/{PG['dbname']}",
)
