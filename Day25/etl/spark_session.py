from pyspark.sql import SparkSession

# Scala 2.13 build (Spark 4.x). The Snowflake JDBC driver is pulled in as a dependency.
# On Spark 3.5 with Scala 2.12 use net.snowflake:spark-snowflake_2.12:3.1.1 instead.
SNOWFLAKE_PACKAGE = "net.snowflake:spark-snowflake_2.13:3.1.1"


def get_spark(app_name="hospital_etl", master=None, with_snowflake=False):
    builder = (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.ansi.enabled", "false")  # bad casts become null instead of errors
        .config("spark.sql.session.timeZone", "UTC")
    )
    if master:
        builder = builder.master(master)
    if with_snowflake:
        builder = builder.config("spark.jars.packages", SNOWFLAKE_PACKAGE)
    return builder.getOrCreate()
