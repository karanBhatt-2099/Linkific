# CRUD = Create, Read, Update, Delete using the ORM
from models import Session, Employee

session = Session()
session.query(Employee).delete()   # start clean
session.commit()

# CREATE
session.add(Employee(name="Asha", department="Engineering", salary=85000))
session.add_all([
    Employee(name="Ravi", department="Sales", salary=55000),
    Employee(name="Neha", department="Sales", salary=60000),
    Employee(name="Karan", department="HR", salary=48000),
])
session.commit()

# READ
print("All:", session.query(Employee).all())
print("First:", session.query(Employee).first())
print("By id 1:", session.get(Employee, 1))

# QUERYING
print("Sales:", session.query(Employee).filter(Employee.department == "Sales").all())
print("Salary > 50000:", session.query(Employee).filter(Employee.salary > 50000).all())
print("Sorted:", session.query(Employee).order_by(Employee.salary.desc()).all())
print("Count:", session.query(Employee).count())

# UPDATE
emp = session.query(Employee).filter_by(name="Ravi").first()
emp.salary = 70000
session.commit()
print("Updated:", emp)

# DELETE
session.delete(session.query(Employee).filter_by(name="Karan").first())
session.commit()
print("After delete:", session.query(Employee).all())

session.close()
