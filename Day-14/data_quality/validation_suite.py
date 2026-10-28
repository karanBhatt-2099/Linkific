"""Validation suite: runs the DQ framework on raw data and on cleaned data.
Run from the project root:  python data_quality/validation_suite.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spark_setup import get_spark
from data_quality.dq_framework import DataQuality

spark = get_spark("ValidationSuite")


def validate_orders(df, name, report_file):
    dq = DataQuality(df, name)
    dq.min_rows(1000)
    dq.not_null("order_id").unique("order_id")
    dq.not_null("price").in_range("price", 0, 10000)
    dq.in_range("quantity", 1, 100)
    dq.in_set("country", ["India", "USA", "UK", "Germany"])
    dq.matches("order_date", r"^\d{4}-\d{2}-\d{2}")
    return dq.report(save_to=report_file)


# 1) Raw data -> should FAIL (we injected bad rows)
raw = spark.read.csv("data/orders.csv", header=True, inferSchema=True)
validate_orders(raw, "orders_raw", "output/dq_report_raw.json")

# 2) Cleaned data -> should PASS (run process_large_csv.py first)
if os.path.exists("output/clean_orders.csv"):
    clean = spark.read.csv("output/clean_orders.csv", header=True, inferSchema=True)
    validate_orders(clean, "orders_clean", "output/dq_report_clean.json")
else:
    print("\nRun process_large_csv.py first to validate the cleaned data.")

spark.stop()
