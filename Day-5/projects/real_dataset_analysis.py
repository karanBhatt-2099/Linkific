"""Real dataset analysis: restaurant tips (244 real records)."""
import pandas as pd

tips = pd.read_csv("data/tips.csv")

print("Shape:", tips.shape)
print(tips.info(), "\n")
print("Missing values:", tips.isna().sum().sum())
print(tips.describe().round(2), "\n")

# New columns
tips["tip_pct"] = (tips["tip"] / tips["total_bill"] * 100).round(1)
tips["bill_per_person"] = (tips["total_bill"] / tips["size"]).round(2)

# Questions to answer with groupby
print("Q1. Which day earns the most in tips?\n", tips.groupby("day")["tip"].sum().sort_values(ascending=False), "\n")
print("Q2. Do smokers tip a higher % ?\n", tips.groupby("smoker")["tip_pct"].mean().round(1), "\n")
print("Q3. Lunch vs dinner:\n", tips.groupby("time").agg(avg_bill=("total_bill", "mean"), avg_tip_pct=("tip_pct", "mean")).round(2), "\n")
print("Q4. Avg tip % by sex and day:\n", pd.pivot_table(tips, values="tip_pct", index="sex", columns="day", aggfunc="mean").round(1), "\n")
print("Q5. Bigger groups tip how much %?\n", tips.groupby("size")["tip_pct"].mean().round(1), "\n")
print("Correlation bill vs tip:", round(tips["total_bill"].corr(tips["tip"]), 2))

print("\nFINDINGS: tips grow with the bill, but the tip % stays fairly steady (~15-16%).")
