"""Step 4: Performance optimization examples."""
import time
import numpy as np
import pandas as pd

np.random.seed(0)
n = 1_000_000
df = pd.DataFrame({
    "city": np.random.choice(["Mumbai", "Delhi", "Pune", "Chennai"], n),
    "qty": np.random.randint(1, 100, n),         # int64 by default
    "price": np.random.rand(n) * 100,            # float64 by default
})


def mb(frame):
    return frame.memory_usage(deep=True).sum() / 1024 ** 2



# 1. Use appropriate data types
print("--- 1. Data types ---")
print(f"Before: {mb(df):.1f} MB")

small = df.copy()
small["city"] = small["city"].astype("category")   # strings -> category
small["qty"] = small["qty"].astype("int8")         # values 1-99 fit in int8
small["price"] = small["price"].astype("float32")  # less precision is fine
print(f"After : {mb(small):.1f} MB")


# 2. Vectorization vs apply
print("\n--- 2. Vectorization vs apply ---")
sample = df.head(200_000).copy()

t = time.time()
sample["total_apply"] = sample.apply(lambda row: row["qty"] * row["price"], axis=1)
t_apply = time.time() - t

t = time.time()
sample["total_vec"] = sample["qty"] * sample["price"]
t_vec = time.time() - t

print(f"apply     : {t_apply:.3f} sec")
print(f"vectorized: {t_vec:.4f} sec  (~{t_apply / t_vec:.0f}x faster)")

# Conditional logic: use np.where instead of apply
df["size"] = np.where(df["qty"] > 50, "big", "small")


# 3. query() vs boolean indexing
print("\n--- 3. query() vs boolean indexing ---")

t = time.time()
r1 = df[(df["qty"] > 50) & (df["city"] == "Mumbai")]
t_bool = time.time() - t

t = time.time()
r2 = df.query("qty > 50 and city == 'Mumbai'")
t_query = time.time() - t

print(f"boolean indexing: {t_bool:.4f} sec")
print(f"query()         : {t_query:.4f} sec")
print("Same result:", r1.equals(r2))
print("Tip: query() is easier to read; speed is similar for most cases.")


# 4. Category dtype makes groupby faster too
print("\n--- 4. groupby: object vs category ---")
t = time.time()
df.groupby("city")["price"].mean()
t_obj = time.time() - t

t = time.time()
small.groupby("city", observed=True)["price"].mean()
t_cat = time.time() - t
print(f"object  : {t_obj:.4f} sec")
print(f"category: {t_cat:.4f} sec")
