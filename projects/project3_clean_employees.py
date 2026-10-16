"""Project 3: Clean an employee dataset."""
import pandas as pd
import numpy as np

df = pd.read_csv("data/messy_employees.csv")

df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
df = df.drop_duplicates()

# Names: remove extra spaces inside, then Title Case
df["full_name"] = df["full_name"].str.split().str.join(" ").str.title()

# Department: standardise and fill missing
df["department"] = df["department"].str.strip().str.upper().fillna("UNKNOWN")

# Salary: "62,000" -> 62000, "N/A" -> NaN -> fill with department average
df["salary"] = pd.to_numeric(df["salary"].str.replace(",", "", regex=False), errors="coerce")
df["salary"] = df["salary"].fillna(df.groupby("department")["salary"].transform("mean"))
df["salary"] = df["salary"].fillna(df["salary"].mean())   # in case a whole dept was missing

# Dates + experience
df["join_date"] = pd.to_datetime(df["join_date"], format="%d-%m-%Y")
df["years_at_company"] = ((pd.Timestamp("2026-10-16") - df["join_date"]).dt.days / 365).round(1)

df = df.reset_index(drop=True)
print(df.head(), "\n")
print("Salary summary by department:\n", df.groupby("department")["salary"].agg(["count", "mean", "max"]).round(0))

df.to_csv("data/clean_employees.csv", index=False)
print("\nSaved data/clean_employees.csv")
