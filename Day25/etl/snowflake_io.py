"""Everything that talks to Snowflake. The pipeline only uses the four public methods,
so tests can swap this class for an in-memory fake."""
from etl import config
from etl.incremental import build_merge_sql
from etl.logger import get_logger
from etl.retry import retry

log = get_logger(__name__)

SPARK_FORMAT = "net.snowflake.spark.snowflake"


class SnowflakeSink:
    def __init__(self):
        sf = config.SNOWFLAKE
        self.connection_args = {k: v for k, v in sf.items() if v}
        self.spark_options = {
            "sfURL": f"{sf['account']}.snowflakecomputing.com",
            "sfUser": sf["user"],
            "sfPassword": sf["password"],
            "sfDatabase": sf["database"],
            "sfSchema": sf["schema"],
            "sfWarehouse": sf["warehouse"],
        }
        if sf["role"]:
            self.spark_options["sfRole"] = sf["role"]

    # ----- plumbing -----
    def _run(self, sql, params=None):
        import snowflake.connector  # imported here so tests do not need the package

        conn = snowflake.connector.connect(**self.connection_args)
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.fetchall()
        finally:
            conn.close()

    def _write(self, df, table, keep_table=False):
        writer = (
            df.write.format(SPARK_FORMAT)
            .options(**self.spark_options)
            .option("dbtable", table)
            .mode("overwrite")
        )
        if keep_table:  # empty the table instead of dropping it, so grants and DDL survive
            writer = writer.option("truncate_table", "on").option("column_mapping", "name")
        writer.save()

    # ----- public API used by the pipeline -----
    @retry()
    def get_watermark(self, table):
        rows = self._run("SELECT last_updated_at FROM etl_watermark WHERE table_name = %s", (table,))
        return rows[0][0] if rows else None

    @retry()
    def set_watermark(self, table, value):
        self._run(
            "MERGE INTO etl_watermark t USING (SELECT %s AS table_name, %s AS last_updated_at) s "
            "ON t.table_name = s.table_name "
            "WHEN MATCHED THEN UPDATE SET t.last_updated_at = s.last_updated_at, t.loaded_at = CURRENT_TIMESTAMP() "
            "WHEN NOT MATCHED THEN INSERT (table_name, last_updated_at, loaded_at) "
            "VALUES (s.table_name, s.last_updated_at, CURRENT_TIMESTAMP())",
            (table, value),
        )

    @retry()
    def upsert(self, df, table, keys):
        """Write the changed rows to a staging table, then MERGE them into the target."""
        staging = f"{table}_STG"
        self._write(df, staging)
        columns = [c for c in df.columns if c != "is_deleted"]
        self._run(build_merge_sql(table, staging, keys, columns))
        log.info("Merged into %s", table)

    @retry()
    def replace(self, df, table):
        """Full refresh of a small table (used for the summary)."""
        self._write(df, table, keep_table=True)
        log.info("Replaced %s", table)
