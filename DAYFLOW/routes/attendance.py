"""
DAYFLOW - Attendance routes (employee self-service).

Check-in / check-out rules enforced here:
  * one check-in per employee per calendar date (DB unique constraint backs this up too)
  * cannot check out before checking in
  * working hours are computed server-side from check_in/check_out times
"""

from datetime import datetime, date

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user

from models import db
from models.attendance import Attendance

attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.before_request
def restrict_area():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    if current_user.is_admin():
        flash('Admins should use the admin attendance view.', 'warning')
        return redirect(url_for('admin.attendance_all'))


@attendance_bp.route('/')
def view_attendance():
    employee = current_user.employee
    records = (
        Attendance.query.filter_by(employee_id=employee.id)
        .order_by(Attendance.date.desc())
        .limit(30)
        .all()
    )
    today_record = Attendance.query.filter_by(employee_id=employee.id, date=date.today()).first()
    return render_template('attendance.html', records=records, today_record=today_record)


@attendance_bp.route('/check-in', methods=['POST'])
def check_in():
    employee = current_user.employee
    today = date.today()

    existing = Attendance.query.filter_by(employee_id=employee.id, date=today).first()
    if existing:
        flash('You have already checked in today.', 'warning')
        return redirect(url_for('attendance.view_attendance'))

    record = Attendance(
        employee_id=employee.id,
        date=today,
        check_in=datetime.now().time(),
        status='Present',
    )
    db.session.add(record)
    db.session.commit()
    flash('Checked in successfully.', 'success')
    return redirect(url_for('attendance.view_attendance'))


@attendance_bp.route('/check-out', methods=['POST'])
def check_out():
    employee = current_user.employee
    today = date.today()

    record = Attendance.query.filter_by(employee_id=employee.id, date=today).first()
    if not record or not record.check_in:
        flash('You must check in before checking out.', 'danger')
        return redirect(url_for('attendance.view_attendance'))

    if record.check_out:
        flash('You have already checked out today.', 'warning')
        return redirect(url_for('attendance.view_attendance'))

    now = datetime.now().time()
    record.check_out = now

    checkin_dt = datetime.combine(today, record.check_in)
    checkout_dt = datetime.combine(today, now)
    hours = (checkout_dt - checkin_dt).total_seconds() / 3600
    record.working_hours = round(hours, 2)

    if hours < 4:
        record.status = 'Half-day'

    db.session.commit()
    flash('Checked out successfully.', 'success')
    return redirect(url_for('attendance.view_attendance'))
