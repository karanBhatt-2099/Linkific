-- 02: Synthetic source data (deliberately slightly dirty: casing, spaces, NULL city, orphan customer, qty=0)
USE DATABASE {{DB}};
USE SCHEMA STG;

CREATE OR REPLACE TABLE stg_customers AS
WITH g AS (SELECT SEQ4()+1 AS n FROM TABLE(GENERATOR(ROWCOUNT=>200)))
SELECT 'C'||LPAD(n::STRING,4,'0') AS customer_id,
  IFF(MOD(n,7)=0, UPPER('customer '||n), 'Customer '||n) AS customer_name,
  IFF(MOD(n,10)=0, ' '||UPPER('customer'||n||'@example.com')||' ', 'customer'||n||'@example.com') AS email,
  IFF(MOD(n,25)=0, NULL, DECODE(MOD(ABS(HASH(n,'city')),5),0,'Mumbai',1,'Delhi',2,'Pune',3,'Bengaluru','Chennai')) AS city,
  DECODE(MOD(ABS(HASH(n,'seg')),3),0,'Consumer',1,'Corporate','Home Office') AS segment,
  DATEADD(day, -(30+MOD(ABS(HASH(n,'su')),900)), CURRENT_DATE()) AS signup_date
FROM g;

CREATE OR REPLACE TABLE stg_products AS
WITH g AS (SELECT SEQ4()+1 AS n FROM TABLE(GENERATOR(ROWCOUNT=>50)))
SELECT 'P'||LPAD(n::STRING,3,'0') AS product_id,
  'Product '||n AS product_name,
  DECODE(MOD(ABS(HASH(n,'cat')),4),0,'Electronics',1,'Furniture',2,'Clothing','Grocery') AS category,
  DECODE(MOD(ABS(HASH(n,'br')),3),0,'Acme',1,'Globex','Initech') AS brand,
  ROUND((10+MOD(ABS(HASH(n,'pp')),490))*0.6,2) AS unit_cost,
  (10+MOD(ABS(HASH(n,'pp')),490))::NUMBER(12,2) AS list_price
FROM g;

CREATE OR REPLACE TABLE stg_stores AS
WITH g AS (SELECT SEQ4()+1 AS n FROM TABLE(GENERATOR(ROWCOUNT=>10)))
SELECT 'ST'||LPAD(n::STRING,2,'0') AS store_id,
  'Store '||n AS store_name,
  DECODE(MOD(n,5),0,'Mumbai',1,'Delhi',2,'Pune',3,'Bengaluru','Chennai') AS city,
  DECODE(MOD(n,3),0,'West',1,'North','South') AS region,
  DATEADD(day, -(200+n*50), CURRENT_DATE()) AS open_date
FROM g;

CREATE OR REPLACE TABLE stg_sales AS
WITH g AS (SELECT SEQ4()+1 AS n, FLOOR((SEQ4()+1)/3) AS o FROM TABLE(GENERATOR(ROWCOUNT=>20000)))
SELECT 'S'||LPAD(n::STRING,6,'0') AS sale_id,
  'O'||LPAD(o::STRING,6,'0') AS order_id,
  DATEADD(day, MOD(ABS(HASH(o,'d')),730), '2024-01-01'::DATE) AS order_date,
  IFF(MOD(ABS(HASH(o,'orph')),100)=0, 'C9999',
      'C'||LPAD((MOD(ABS(HASH(o,'c')),200)+1)::STRING,4,'0')) AS customer_id,
  'P'||LPAD((MOD(ABS(HASH(n,'p')),50)+1)::STRING,3,'0') AS product_id,
  'ST'||LPAD((MOD(ABS(HASH(o,'s')),10)+1)::STRING,2,'0') AS store_id,
  IFF(MOD(ABS(HASH(n,'z')),200)=0, 0, MOD(ABS(HASH(n,'q')),5)+1) AS quantity,
  DECODE(MOD(ABS(HASH(n,'dc')),4),0,0,1,5,2,10,15)::NUMBER(5,2) AS discount_pct
FROM g;
