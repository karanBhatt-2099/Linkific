# ORM model: a Python class = a database table
import sys; sys.path.append("..")
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from config import DB_URL

engine = create_engine(DB_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Employee(Base):
    __tablename__ = "orm_employees"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    department = Column(String)
    salary = Column(Integer)

    def __repr__(self):
        return f"<Employee {self.name} | {self.department} | {self.salary}>"

Base.metadata.create_all(engine)   # creates the table
