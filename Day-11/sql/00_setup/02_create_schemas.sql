CREATE SCHEMA IF NOT EXISTS dw;
CREATE SCHEMA IF NOT EXISTS dw_snowflake;
CREATE SCHEMA IF NOT EXISTS scd_demo;

-- Validation: you should see 3 rows (plus system schemas filtered out)
SELECT schema_name
FROM   information_schema.schemata
WHERE  schema_name IN ('dw', 'dw_snowflake', 'scd_demo')
ORDER  BY schema_name;
