"""
DAYFLOW - Attendance model.

One row per employee per calendar date. A unique constraint on
(employee_id, date) is what physically prevents double check-ins.
"""

from models import db

STATUS_PRESENT = 'Present'
STATUS_ABSENT = 'Absent'
STATUS_HALF_DAY = 'Half-day'
STATUS_LEAVE = 'Leave'


class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    check_in = db.Column(db.Time)
    check_out = db.Column(db.Time)
    working_hours = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default=STATUS_PRESENT)

    __table_args__ = (
        db.UniqueConstraint('employee_id', 'date', name='uq_attendance_employee_date'),
    )

    def __repr__(self):
        return f'<Attendance emp={self.employee_id} {self.date} {self.status}>'
