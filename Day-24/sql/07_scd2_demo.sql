-- 07 (optional): change source data, then re-run 04 + 06 to demonstrate SCD2 history
USE DATABASE {{DB}};
UPDATE STG.stg_customers SET city = 'Singapore', segment = 'Corporate'
WHERE customer_id IN ('C0001','C0002','C0003','C0004','C0005');
