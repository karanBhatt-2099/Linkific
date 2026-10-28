"""PySpark basics: select, filter, groupBy, join, window, UDF."""
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.types import StringType
from spark_setup import get_spark

spark = get_spark("Operations")

orders = spark.read.csv("data/orders.csv", header=True, inferSchema=True)
customers = spark.read.csv("data/customers.csv", header=True, inferSchema=True)

print("--- Schema & basics ---")
orders.printSchema()
print("Rows:", orders.count())
orders.show(3)

print("--- Select & filter ---")
orders.select("order_id", "product", "price").show(3)
orders.filter((F.col("country") == "India") & (F.col("price") > 500)).show(3)

print("--- Add column ---")
orders = orders.withColumn("total", F.col("quantity") * F.col("price"))

print("--- GroupBy & aggregation ---")
(orders.groupBy("category")
       .agg(F.count("*").alias("orders"),
            F.round(F.sum("total"), 2).alias("revenue"),
            F.round(F.avg("price"), 2).alias("avg_price"))
       .orderBy(F.desc("revenue"))
       .show())

print("--- Join ---")
joined = orders.join(customers, on="customer_id", how="inner")
joined.select("order_id", "name", "city", "total").show(3)

print("--- Window function: rank products by revenue within each category ---")
product_rev = orders.groupBy("category", "product").agg(F.sum("total").alias("revenue"))
w = Window.partitionBy("category").orderBy(F.desc("revenue"))
product_rev.withColumn("rank", F.rank().over(w)).show()

print("--- UDF ---")
def price_label(p):
    if p is None:
        return "unknown"
    return "cheap" if p < 100 else "medium" if p < 500 else "expensive"

price_label_udf = F.udf(price_label, StringType())
orders.withColumn("label", price_label_udf("price")).select("price", "label").show(5)

spark.stop()
