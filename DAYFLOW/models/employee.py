"""
DAYFLOW - Employee model.

Holds the employee's personal / job details. Linked 1-to-1 with a User
(login account) and 1-to-many with Attendance, Leave and Payroll records.
"""

from datetime import datetime

from models import db


class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    department = db.Column(db.String(50))
    designation = db.Column(db.String(50))
    joining_date = db.Column(db.Date)
    profile_picture = db.Column(db.String(255), default='default.png')
    documents = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attendances = db.relationship('Attendance', backref='employee', cascade='all, delete-orphan')
    leaves = db.relationship('Leave', backref='employee', cascade='all, delete-orphan')
    payrolls = db.relationship('Payroll', backref='employee', cascade='all, delete-orphan')

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __repr__(self):
        return f'<Employee {self.employee_id} {self.full_name}>'
