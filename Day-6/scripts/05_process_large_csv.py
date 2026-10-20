"""Step 5: Process a large CSV in chunks (never loads the whole file in memory)."""
import pandas as pd

FILE = "data/big_file.csv"

# Read only the columns we need, with small dtypes
dtypes = {"city": "category", "amount": "float32", "qty": "int8"}

total_rows = 0
partial_sums = []

# chunksize = rows per chunk
for chunk in pd.read_csv(FILE, usecols=["city", "amount", "qty"],
                         dtype=dtypes, chunksize=100_000):
    total_rows += len(chunk)
    # aggregate each chunk, keep only the small result
    partial_sums.append(chunk.groupby("city", observed=True)["amount"].agg(["sum", "count"]))

# Combine the small results
combined = pd.concat(partial_sums).groupby(level=0).sum()
combined["average"] = combined["sum"] / combined["count"]

print("Rows processed:", total_rows)
print(combined.round(2))

combined.to_csv("output/big_file_summary.csv")
print("Saved -> output/big_file_summary.csv")
