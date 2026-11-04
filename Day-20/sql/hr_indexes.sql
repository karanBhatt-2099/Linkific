CREATE INDEX idx_emp_dept     ON employees(dept_id);
CREATE INDEX idx_emp_manager  ON employees(manager_id);
CREATE INDEX idx_att_emp      ON attendance(emp_id);
CREATE INDEX idx_att_date     ON attendance(work_date);
