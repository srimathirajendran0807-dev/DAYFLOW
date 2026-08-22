"""
DAYFLOW - Leave model.
"""

from datetime import datetime

from models import db

LEAVE_TYPES = ('Paid', 'Sick', 'Unpaid')
LEAVE_STATUSES = ('Pending', 'Approved', 'Rejected')


class Leave(db.Model):
    __tablename__ = 'leaves'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    leave_type = db.Column(db.String(20), nullable=False)
    from_date = db.Column(db.Date, nullable=False)
    to_date = db.Column(db.Date, nullable=False)
    remarks = db.Column(db.String(255))
    status = db.Column(db.String(20), default='Pending')
    admin_comment = db.Column(db.String(255))
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)

    @property
    def total_days(self):
        return (self.to_date - self.from_date).days + 1

    def __repr__(self):
        return f'<Leave emp={self.employee_id} {self.leave_type} {self.status}>'
