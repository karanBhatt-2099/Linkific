CREATE TABLE customers (
  customer_id INT PRIMARY KEY,
  name TEXT, email TEXT, city TEXT, updated_at TIMESTAMP
);
INSERT INTO customers VALUES
 (1,'Leanne Graham','Sincere@april.biz','Mumbai','2025-01-10 10:00:00'),
 (2,'Ervin Howell','Shanna@melissa.tv','Delhi','2025-01-11 09:30:00'),
 (3,'Clementine Bauch','Nathan@yesenia.net','Chennai','2025-01-12 14:00:00'),
 (4,'Asha Rao','asha@example.com','Bengaluru','2025-01-13 08:00:00'),
 (5,'Ravi Kumar','ravi@example.com','Hyderabad','2025-01-14 12:00:00');

CREATE TABLE orders (
  order_id INT PRIMARY KEY,
  customer_id INT, amount NUMERIC(10,2), order_date DATE
);
INSERT INTO orders VALUES
 (1001,1,250.00,'2025-02-01'),
 (1002,2,120.50,'2025-02-02'),
 (1003,3,999.99,'2025-02-03'),
 (1004,4,75.00,'2025-02-04'),
 (1005,5,310.25,'2025-02-05');
