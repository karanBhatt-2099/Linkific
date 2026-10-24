-- =====================================================================
-- run_all.sql  (OPTIONAL shortcut for the psql command line / VS Code terminal)
-- Runs every script in the right order. It uses psql meta-commands (\i),
-- so it does NOT work inside pgAdmin's Query Tool - in pgAdmin run the
-- files one by one, as the README explains.
--
--   cd sql
--   psql -U postgres -d sales_dw -f run_all.sql
--   (create the database first:  psql -U postgres -c "CREATE DATABASE sales_dw")
-- =====================================================================
\set ON_ERROR_STOP on
\i 00_setup/02_create_schemas.sql
\i 01_ddl/01_create_dimensions.sql
\i 01_ddl/02_create_fact_sales.sql
\i 01_ddl/03_create_snowflake_schema.sql
\i 01_ddl/04_create_galaxy_fact_inventory.sql
\i 02_data/01_load_dimensions.sql
\i 02_data/02_load_fact_sales.sql
\i 02_data/03_load_snowflake_and_galaxy.sql
\i 03_scd/01_scd_type1_overwrite.sql
\i 03_scd/02_scd_type2_history.sql
\i 03_scd/03_scd_type3_previous_value.sql
\i 04_validation/01_validate_star_schema.sql
\i 04_validation/02_validate_scd.sql
