"""PySpark setup. Install first:  pip install pyspark
(Java 8/11/17/21 must also be installed.)"""
import os, sys
from pyspark.sql import SparkSession

# Use the same Python that runs this script (fixes Windows 'python3' warning)
os.environ["PYSPARK_PYTHON"] = sys.executable


def get_spark(app_name="Day14"):
    return (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")                          # use all CPU cores
        .config("spark.sql.shuffle.partitions", "4")  # small number = faster locally
        .getOrCreate()
    )


if __name__ == "__main__":
    spark = get_spark("SetupTest")
    print("Spark version:", spark.version)
    spark.range(5).show()      # runs fully inside Spark, no Python worker
    spark.stop()
