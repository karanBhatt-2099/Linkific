-- 03: Date dimension 2020-01-01 .. 2030-12-31 (4018 days), hierarchies, holiday flags
USE DATABASE {{DB}};
USE SCHEMA DW;

TRUNCATE TABLE dim_date;

INSERT INTO dim_date (date_key, full_date, day_of_month, day_of_week, day_name, day_of_year, week_of_year,
  month_num, month_name, year_month, quarter_num, quarter_name, year_num, fiscal_year, fiscal_quarter,
  month_start_date, month_end_date, is_weekend)
WITH d AS (SELECT DATEADD(day, SEQ4(), '2020-01-01'::DATE) AS dt FROM TABLE(GENERATOR(ROWCOUNT=>4018)))
SELECT TO_NUMBER(TO_CHAR(dt,'YYYYMMDD')), dt, DAY(dt), DAYOFWEEKISO(dt),
  DECODE(DAYOFWEEKISO(dt),1,'Monday',2,'Tuesday',3,'Wednesday',4,'Thursday',5,'Friday',6,'Saturday','Sunday'),
  DAYOFYEAR(dt), WEEKISO(dt), MONTH(dt), TO_CHAR(dt,'MMMM'), TO_CHAR(dt,'YYYY-MM'),
  QUARTER(dt), 'Q'||QUARTER(dt), YEAR(dt),
  IFF(MONTH(dt)>=4, YEAR(dt)+1, YEAR(dt)),
  CEIL(((MONTH(dt)+8)%12+1)/3.0),                   -- Apr-Jun=1 ... Jan-Mar=4
  DATE_TRUNC('month',dt), LAST_DAY(dt,'month'),
  DAYOFWEEKISO(dt) IN (6,7)
FROM d;

-- Holiday flags (fixed-date holidays; movable ones such as Diwali/Holi/Easter must be added from a calendar source)
MERGE INTO dim_date t
USING (SELECT * FROM VALUES
  (1,1,'New Year''s Day'),(1,26,'Republic Day'),(5,1,'Labour Day'),
  (8,15,'Independence Day'),(10,2,'Gandhi Jayanti'),(12,25,'Christmas Day')
  AS h(m,d,name)) s
ON t.month_num = s.m AND t.day_of_month = s.d
WHEN MATCHED THEN UPDATE SET t.is_holiday = TRUE, t.holiday_name = s.name;
