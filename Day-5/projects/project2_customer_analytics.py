"""Project 2: Clean customers, then analyse them."""
import pandas as pd

df = pd.read_csv("data/messy_customers.csv")

# ----- Cleaning -----
df = df.drop_duplicates()
df["name"] = df["name"].str.strip().str.title()
df["email"] = df["email"].str.strip().str.lower()
df["city"] = df["city"].str.strip().str.title()
df["age"] = df["age"].fillna(df["age"].median())
df["city"] = df["city"].fillna("Unknown")
df["email"] = df["email"].fillna("no-email")
df["signup_date"] = pd.to_datetime(df["signup_date"], format="%d/%m/%Y")
df = df.reset_index(drop=True)

# ----- Analytics -----
# Age groups
df["age_group"] = pd.cut(df["age"], bins=[0, 30, 50, 100], labels=["Young", "Adult", "Senior"])

# Spending tiers (quartiles)
df["spend_tier"] = pd.qcut(df["total_spent"], q=3, labels=["Low", "Medium", "High"])

print("Customers per city:\n", df["city"].value_counts(), "\n")
print("Average spend by age group:\n", df.groupby("age_group", observed=True)["total_spent"].mean().round(0), "\n")
print("Age group vs spend tier:\n", pd.crosstab(df["age_group"], df["spend_tier"]), "\n")
print("Top 5 customers:\n", df.nlargest(5, "total_spent")[["name", "city", "total_spent"]])

df.to_csv("data/clean_customers.csv", index=False)
print("\nSaved data/clean_customers.csv")
