"""Project 1: Clean a messy sales dataset."""
import pandas as pd

df = pd.read_csv("data/messy_sales.csv")
print("BEFORE:", df.shape)
print(df.dtypes, "\n")

# 1. Clean column names
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# 2. Remove duplicate rows
print("Duplicates:", df.duplicated().sum())
df = df.drop_duplicates()

# 3. Clean text columns
df["customer_name"] = df["customer_name"].str.strip().str.title()
df["product"] = df["product"].str.strip().str.title()

# 4. Fix numbers ("$599" -> 599)
df["price"] = pd.to_numeric(df["price"].astype(str).str.replace("$", "", regex=False), errors="coerce")
df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")

# 5. Fix dates (bad ones become NaT)
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

# 6. Missing values
df["quantity"] = df["quantity"].fillna(1)
df["region"] = df["region"].fillna("Unknown")
df = df.dropna(subset=["order_date"])

# 7. New column
df["revenue"] = df["quantity"] * df["price"]
df = df.reset_index(drop=True)

print("AFTER:", df.shape)
print(df.head(), "\n")
print("Revenue by product:\n", df.groupby("product")["revenue"].sum().sort_values(ascending=False))

df.to_csv("data/clean_sales.csv", index=False)
print("\nSaved data/clean_sales.csv")
