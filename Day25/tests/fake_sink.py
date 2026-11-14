class FakeSink:
    """In-memory stand-in for SnowflakeSink with the same MERGE behaviour."""

    def __init__(self):
        self.tables = {}      # table name -> {key tuple: row dict}
        self.watermarks = {}  # table name -> 'yyyy-MM-dd HH:mm:ss'
        self.fail_upserts = False
        self.upsert_log = []  # (table, number of rows) for every upsert call

    def get_watermark(self, table):
        return self.watermarks.get(table)

    def set_watermark(self, table, value):
        self.watermarks[table] = value

    def upsert(self, df, table, keys):
        if self.fail_upserts:
            raise RuntimeError("simulated Snowflake outage")
        rows = self.tables.setdefault(table, {})
        records = df.collect()
        self.upsert_log.append((table, len(records)))
        for record in records:
            row = record.asDict()
            key = tuple(row[k] for k in keys)
            if row["is_deleted"]:
                rows.pop(key, None)  # WHEN MATCHED AND is_deleted THEN DELETE
            else:
                rows[key] = {k: v for k, v in row.items() if k != "is_deleted"}

    def replace(self, df, table):
        self.tables[table] = {i: record.asDict() for i, record in enumerate(df.collect())}

    def rows(self, table):
        return list(self.tables.get(table, {}).values())
