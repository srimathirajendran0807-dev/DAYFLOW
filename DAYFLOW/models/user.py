"""
DAYFLOW - User model.

Holds login credentials and role. Each User has exactly one Employee
profile with the actual personal / job details.
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from models import db

ROLE_EMPLOYEE = 'employee'
ROLE_ADMIN = 'admin'


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=ROLE_EMPLOYEE)
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship(
        'Employee', backref='user', uselist=False, cascade='all, delete-orphan'
    )
    notifications = db.relationship(
        'Notification', backref='user', cascade='all, delete-orphan',
        order_by='Notification.created_at.desc()'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == ROLE_ADMIN

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


class Notification(db.Model):
    """
    Simple per-user notification log. Not part of the originally listed
    table set, but required by the Notifications feature (leave submitted /
    approved / rejected, payroll updated, etc.), so it lives alongside User.
    """
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Notification {self.id} user={self.user_id}>'
