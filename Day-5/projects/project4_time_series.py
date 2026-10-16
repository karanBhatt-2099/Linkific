"""Project 4: Time series manipulation on the clean sales data."""
import pandas as pd

df = pd.read_csv("data/clean_sales.csv", parse_dates=["order_date"])

# Date parts
df["year"] = df["order_date"].dt.year
df["month"] = df["order_date"].dt.month
df["weekday"] = df["order_date"].dt.day_name()

# Use the date as the index, then resample
ts = df.set_index("order_date").sort_index()
monthly = ts["revenue"].resample("ME").sum()        # ME = month end
print("Monthly revenue:\n", monthly, "\n")

# Moving average + growth
monthly_df = monthly.to_frame("revenue")
monthly_df["moving_avg_2"] = monthly_df["revenue"].rolling(2).mean()
monthly_df["growth_%"] = (monthly_df["revenue"].pct_change() * 100).round(1)
monthly_df["cumulative"] = monthly_df["revenue"].cumsum()
print(monthly_df, "\n")

# Slice by date
print("Revenue Jan-Feb 2024:", ts.loc["2024-01":"2024-02", "revenue"].sum())
print("Revenue by weekday:\n", df.groupby("weekday")["revenue"].sum().sort_values(ascending=False))
