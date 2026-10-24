SELECT 'SCD1: Priya overwritten to Surat, 4 rows' AS check_name,
       CASE WHEN (SELECT COUNT(*) FROM scd_demo.customer_scd1)=4
             AND (SELECT city FROM scd_demo.customer_scd1 WHERE customer_id='C002')='Surat'
            THEN 'PASS' ELSE 'FAIL' END AS status
UNION ALL
SELECT 'SCD2: Aarav has 2 versions, only 1 current (Pune)',
       CASE WHEN (SELECT COUNT(*) FROM scd_demo.customer_scd2 WHERE customer_id='C001')=2
             AND (SELECT city FROM scd_demo.customer_scd2 WHERE customer_id='C001' AND is_current)='Pune'
            THEN 'PASS' ELSE 'FAIL' END
UNION ALL
SELECT 'SCD2: no overlapping date ranges',
       CASE WHEN (SELECT COUNT(*) FROM scd_demo.customer_scd2 a
                  JOIN scd_demo.customer_scd2 b
                    ON a.customer_id=b.customer_id AND a.customer_key<b.customer_key
                   AND a.effective_date <= b.end_date AND b.effective_date <= a.end_date)=0
            THEN 'PASS' ELSE 'FAIL' END
UNION ALL
SELECT 'SCD2: history preserved in facts (Mumbai=5000, Pune=7000)',
       CASE WHEN (SELECT SUM(f.amount) FROM scd_demo.fact_orders_scd2 f
                  JOIN scd_demo.customer_scd2 c USING (customer_key) WHERE c.city='Mumbai')=5000
             AND (SELECT SUM(f.amount) FROM scd_demo.fact_orders_scd2 f
                  JOIN scd_demo.customer_scd2 c USING (customer_key) WHERE c.city='Pune')=7000
            THEN 'PASS' ELSE 'FAIL' END
UNION ALL
SELECT 'SCD3: Priya current=Vadodara, previous=Surat',
       CASE WHEN (SELECT current_city||'/'||previous_city FROM scd_demo.customer_scd3
                  WHERE customer_id='C002')='Vadodara/Surat'
            THEN 'PASS' ELSE 'FAIL' END;
