"""Process the large CSV with Spark: read -> clean -> aggregate -> save as Parquet."""
import os
import time
from pyspark.sql import functions as F
from spark_setup import get_spark

spark = get_spark("ProcessLargeCSV")
start = time.time()

# 1. Read
df = spark.read.csv("data/orders.csv", header=True, inferSchema=True)
print("Raw rows:", df.count())

# 2. Clean
clean = (df.dropDuplicates(["order_id"])                 # remove duplicate IDs
           .dropna(subset=["price"])                       # remove missing price
           .filter(F.col("quantity") > 0)                  # remove bad quantity
           .filter(F.col("country") != "Mars")             # remove invalid country
           .withColumn("total", F.col("quantity") * F.col("price"))
           .withColumn("month", F.month("order_date")))
print("Clean rows:", clean.count())

# 3. Aggregate: monthly revenue per country
monthly = (clean.groupBy("country", "month")
                .agg(F.round(F.sum("total"), 2).alias("revenue"),
                     F.count("*").alias("orders"))
                .orderBy("country", "month"))
monthly.show(10)

# 4. Save with pandas (avoids the Windows "winutils.exe" problem with Spark writes)
# On Linux/Mac/Databricks you can use: clean.write.parquet("output/clean_orders")
os.makedirs("output", exist_ok=True)
clean.toPandas().to_csv("output/clean_orders.csv", index=False)
monthly.toPandas().to_csv("output/monthly_revenue.csv", index=False)

print(f"Done in {time.time() - start:.1f} seconds")
spark.stop()
