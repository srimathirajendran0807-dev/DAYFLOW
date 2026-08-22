"""
DAYFLOW - Payroll model.

net_salary is always recomputed server-side from basic_salary + allowances
- deductions via calculate_net() -- it is never trusted from a client form.
"""

from datetime import datetime

from models import db


class Payroll(db.Model):
    __tablename__ = 'payroll'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    basic_salary = db.Column(db.Float, nullable=False, default=0.0)
    allowances = db.Column(db.Float, default=0.0)
    deductions = db.Column(db.Float, default=0.0)
    net_salary = db.Column(db.Float, default=0.0)
    pay_month = db.Column(db.Integer, nullable=False)   # 1-12
    pay_year = db.Column(db.Integer, nullable=False)
    salary_slip = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('employee_id', 'pay_month', 'pay_year', name='uq_payroll_employee_month_year'),
    )

    def calculate_net(self):
        self.net_salary = (self.basic_salary or 0) + (self.allowances or 0) - (self.deductions or 0)
        return self.net_salary

    def __repr__(self):
        return f'<Payroll emp={self.employee_id} {self.pay_month}/{self.pay_year}>'
