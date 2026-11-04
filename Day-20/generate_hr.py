"""HR data: departments -> employees (with managers) -> attendance"""
import random
from datetime import date, timedelta
from faker import Faker
from config import write_csv

random.seed(7)
Faker.seed(7)
fake = Faker("en_IN")
DB = "hr_db"
TODAY = date(2026, 11, 1)
N_EMPLOYEES, ATTENDANCE_DAYS = 1000, 180

# dept -> (location, [(job title, min salary, max salary)])
depts = {
    "Engineering": ("Mumbai", [("Software Engineer", 600000, 1800000), ("QA Engineer", 400000, 1000000)]),
    "Sales": ("Delhi", [("Sales Executive", 300000, 900000), ("Account Manager", 500000, 1400000)]),
    "HR": ("Pune", [("HR Executive", 300000, 800000), ("Recruiter", 350000, 900000)]),
    "Finance": ("Mumbai", [("Accountant", 400000, 1000000), ("Financial Analyst", 600000, 1500000)]),
    "Marketing": ("Bengaluru", [("Marketing Executive", 350000, 1000000), ("Content Writer", 300000, 800000)]),
    "Operations": ("Chennai", [("Operations Associate", 300000, 800000), ("Supply Planner", 450000, 1200000)]),
    "Support": ("Hyderabad", [("Support Agent", 250000, 600000), ("Team Lead", 500000, 1000000)]),
    "Legal": ("Delhi", [("Legal Associate", 600000, 1500000)]),
    "IT": ("Bengaluru", [("System Admin", 450000, 1200000), ("Network Engineer", 450000, 1200000)]),
    "Procurement": ("Pune", [("Buyer", 350000, 900000)]),
}
dept_names = list(depts)

departments = [[i + 1, name, depts[name][0]] for i, name in enumerate(dept_names)]
write_csv(DB, "departments", ["dept_id", "name", "location"], departments)

# Employees. The first 10 employees are department heads (no manager).
employees = []
head_of = {}
for eid in range(1, N_EMPLOYEES + 1):
    if eid <= len(dept_names):
        dept_id, manager_id, title = eid, None, "Department Head"
        low, high = 2500000, 4500000
        head_of[dept_id] = eid
        hire = date(2015, 1, 1) + timedelta(days=random.randint(0, 365))
    else:
        dept_id = random.randint(1, len(dept_names))
        manager_id = head_of[dept_id]
        title, low, high = random.choice(depts[dept_names[dept_id - 1]][1])
        hire = date(2016, 1, 1) + timedelta(days=random.randint(0, (date(2026, 9, 1) - date(2016, 1, 1)).days))
    first, last = fake.first_name(), fake.last_name()
    status = random.choices(["active", "resigned"], [92, 8])[0]
    employees.append([eid, first, last, f"{first}.{last}{eid}@company.com".lower(), hire,
                      title, dept_id, manager_id, round(random.uniform(low, high), 2), status])
write_csv(DB, "employees", ["emp_id", "first_name", "last_name", "email", "hire_date", "job_title",
                            "dept_id", "manager_id", "salary", "status"], employees)

# Attendance for the last 180 days (weekdays only, never before hire date)
attendance = []
att_id = 1
start = TODAY - timedelta(days=ATTENDANCE_DAYS)
for emp in employees:
    day = max(start, emp[4])
    while day < TODAY:
        if day.weekday() < 5:
            status = random.choices(["present", "remote", "leave", "absent"], [85, 7, 5, 3])[0]
            hours = round(random.uniform(7, 9.5), 2) if status in ("present", "remote") else 0
            attendance.append([att_id, emp[0], day, status, hours])
            att_id += 1
        day += timedelta(days=1)
write_csv(DB, "attendance", ["att_id", "emp_id", "work_date", "status", "hours_worked"], attendance)
