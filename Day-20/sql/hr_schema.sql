CREATE TABLE departments (
    dept_id  SERIAL PRIMARY KEY,
    name     VARCHAR(60) UNIQUE NOT NULL,
    location VARCHAR(60)
);
CREATE TABLE employees (
    emp_id     SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name  VARCHAR(50) NOT NULL,
    email      VARCHAR(120) UNIQUE NOT NULL,
    hire_date  DATE NOT NULL,
    job_title  VARCHAR(60) NOT NULL,
    dept_id    INT NOT NULL REFERENCES departments(dept_id),
    manager_id INT REFERENCES employees(emp_id),
    salary     NUMERIC(10,2) NOT NULL CHECK (salary > 0),
    status     VARCHAR(15) NOT NULL
);
CREATE TABLE attendance (
    att_id       SERIAL PRIMARY KEY,
    emp_id       INT NOT NULL REFERENCES employees(emp_id),
    work_date    DATE NOT NULL,
    status       VARCHAR(15) NOT NULL,
    hours_worked NUMERIC(4,2) NOT NULL
);
