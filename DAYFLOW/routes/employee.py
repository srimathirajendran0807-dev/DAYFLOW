"""
DAYFLOW - Employee-facing routes.

Everything under this blueprint is scoped to current_user's own Employee
record. Admins are redirected away (they have their own equivalent views).
"""

import os

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
from werkzeug.utils import secure_filename
from datetime import date

from models import db
from models.attendance import Attendance
from models.leave import Leave
from models.payroll import Payroll
from models.user import Notification

employee_bp = Blueprint('employee', __name__)

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


@employee_bp.before_request
def restrict_to_employee_area():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    if current_user.is_admin():
        flash('Admins do not have an employee self-service area.', 'warning')
        return redirect(url_for('admin.dashboard'))


@employee_bp.route('/dashboard')
def dashboard():
    employee = current_user.employee
    today = date.today()

    today_attendance = Attendance.query.filter_by(employee_id=employee.id, date=today).first()
    pending_leaves = Leave.query.filter_by(employee_id=employee.id, status='Pending').count()
    latest_payroll = (
        Payroll.query.filter_by(employee_id=employee.id)
        .order_by(Payroll.pay_year.desc(), Payroll.pay_month.desc())
        .first()
    )
    notifications = (
        Notification.query.filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(5)
        .all()
    )
    recent_leaves = (
        Leave.query.filter_by(employee_id=employee.id)
        .order_by(Leave.applied_at.desc())
        .limit(3)
        .all()
    )

    return render_template(
        'employee_dashboard.html',
        employee=employee,
        today_attendance=today_attendance,
        pending_leaves=pending_leaves,
        latest_payroll=latest_payroll,
        notifications=notifications,
        recent_leaves=recent_leaves,
    )


@employee_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    employee = current_user.employee

    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()

        cleaned_phone = phone.replace('+', '').replace('-', '').replace(' ', '')
        if phone and not cleaned_phone.isdigit():
            flash('Please enter a valid phone number.', 'danger')
            return render_template('profile.html', employee=employee)

        employee.phone = phone
        employee.address = address

        picture = request.files.get('profile_picture')
        if picture and picture.filename:
            ext = picture.filename.rsplit('.', 1)[-1].lower() if '.' in picture.filename else ''
            if ext not in ALLOWED_IMAGE_EXTENSIONS:
                flash('Profile picture must be a PNG, JPG or GIF file.', 'danger')
                return render_template('profile.html', employee=employee)

            filename = secure_filename(f'user_{current_user.id}.{ext}')
            upload_dir = os.path.join('static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            picture.save(os.path.join(upload_dir, filename))
            employee.profile_picture = filename

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('employee.profile'))

    return render_template('profile.html', employee=employee)


@employee_bp.route('/payroll')
def payroll():
    employee = current_user.employee
    records = (
        Payroll.query.filter_by(employee_id=employee.id)
        .order_by(Payroll.pay_year.desc(), Payroll.pay_month.desc())
        .all()
    )
    return render_template('payroll.html', records=records, is_admin=False)


@employee_bp.route('/notifications/mark-read/<int:notif_id>', methods=['POST'])
def mark_notification_read(notif_id):
    notif = Notification.query.filter_by(id=notif_id, user_id=current_user.id).first()
    if notif:
        notif.is_read = True
        db.session.commit()
    return redirect(request.referrer or url_for('employee.dashboard'))
