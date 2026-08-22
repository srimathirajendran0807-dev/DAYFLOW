"""
DAYFLOW - Leave routes (employee self-service).
"""

from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user

from models import db
from models.leave import Leave, LEAVE_TYPES
from models.user import Notification

leave_bp = Blueprint('leave', __name__)


@leave_bp.before_request
def restrict_area():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    if current_user.is_admin():
        flash('Admins should use the admin leave management view.', 'warning')
        return redirect(url_for('admin.leave_requests'))


@leave_bp.route('/')
def view_leaves():
    employee = current_user.employee
    records = Leave.query.filter_by(employee_id=employee.id).order_by(Leave.applied_at.desc()).all()
    return render_template('leave.html', records=records)


@leave_bp.route('/apply', methods=['POST'])
def apply_leave():
    employee = current_user.employee

    leave_type = request.form.get('leave_type')
    from_date_str = request.form.get('from_date')
    to_date_str = request.form.get('to_date')
    remarks = request.form.get('remarks', '').strip()

    if leave_type not in LEAVE_TYPES:
        flash('Please select a valid leave type.', 'danger')
        return redirect(url_for('leave.view_leaves'))

    try:
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        flash('Please provide valid dates.', 'danger')
        return redirect(url_for('leave.view_leaves'))

    if to_date < from_date:
        flash('End date cannot be before the start date.', 'danger')
        return redirect(url_for('leave.view_leaves'))

    record = Leave(
        employee_id=employee.id,
        leave_type=leave_type,
        from_date=from_date,
        to_date=to_date,
        remarks=remarks,
        status='Pending',
    )
    db.session.add(record)
    db.session.commit()

    # Notify the employee themself as a submission receipt
    db.session.add(Notification(
        user_id=current_user.id,
        message=f'Your {leave_type} leave request ({from_date} to {to_date}) has been submitted and is pending approval.'
    ))
    db.session.commit()

    flash('Leave request submitted successfully.', 'success')
    return redirect(url_for('leave.view_leaves'))
