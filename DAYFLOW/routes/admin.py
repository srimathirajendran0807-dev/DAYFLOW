"""
DAYFLOW - Admin / HR routes.

Everything under this blueprint requires role == 'admin'. Plain employees
are redirected out in restrict_to_admin().
"""

from datetime import date, datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user

from models import db
from models.user import Notification
from models.employee import Employee
from models.attendance import Attendance
from models.leave import Leave
from models.payroll import Payroll

admin_bp = Blueprint('admin', __name__)


@admin_bp.before_request
def restrict_to_admin():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    if not current_user.is_admin():
        flash('You do not have permission to access the admin area.', 'danger')
        return redirect(url_for('employee.dashboard'))


def _notify(user_id, message):
    db.session.add(Notification(user_id=user_id, message=message))


@admin_bp.route('/dashboard')
def dashboard():
    today = date.today()
    total_employees = Employee.query.count()
    present_today = Attendance.query.filter_by(date=today, status='Present').count()
    marked_today = Attendance.query.filter_by(date=today).count()
    absent_today = max(total_employees - marked_today, 0)
    on_leave_today = Leave.query.filter(
        Leave.status == 'Approved', Leave.from_date <= today, Leave.to_date >= today
    ).count()
    pending_leaves = Leave.query.filter_by(status='Pending').count()

    recent_leaves = Leave.query.filter_by(status='Pending').order_by(Leave.applied_at.desc()).limit(5).all()
    employees = Employee.query.order_by(Employee.created_at.desc()).limit(6).all()

    return render_template(
        'admin_dashboard.html',
        view='dashboard',
        total_employees=total_employees,
        present_today=present_today,
        absent_today=absent_today,
        on_leave=on_leave_today,
        pending_leaves=pending_leaves,
        recent_leaves=recent_leaves,
        employees=employees,
    )


@admin_bp.route('/employees')
def employee_list():
    employees = Employee.query.order_by(Employee.first_name).all()
    return render_template('admin_dashboard.html', view='employees', employees_full=employees)


@admin_bp.route('/employees/<int:emp_id>', methods=['GET', 'POST'])
def employee_detail(emp_id):
    employee = Employee.query.get_or_404(emp_id)

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()

        if not first_name or not last_name:
            flash('First and last name cannot be empty.', 'danger')
            return render_template('profile.html', employee=employee, admin_view=True)

        employee.first_name = first_name
        employee.last_name = last_name
        employee.phone = request.form.get('phone', '').strip()
        employee.address = request.form.get('address', '').strip()
        employee.department = request.form.get('department', '').strip()
        employee.designation = request.form.get('designation', '').strip()

        dob = request.form.get('date_of_birth')
        if dob:
            try:
                employee.date_of_birth = datetime.strptime(dob, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date of birth format.', 'danger')
                return render_template('profile.html', employee=employee, admin_view=True)

        db.session.commit()
        flash('Employee details updated.', 'success')
        return redirect(url_for('admin.employee_detail', emp_id=emp_id))

    return render_template('profile.html', employee=employee, admin_view=True)


@admin_bp.route('/attendance')
def attendance_all():
    selected_date_str = request.args.get('date')
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()

    records = (
        db.session.query(Attendance, Employee)
        .join(Employee, Attendance.employee_id == Employee.id)
        .filter(Attendance.date == selected_date)
        .all()
    )
    return render_template(
        'attendance.html', admin_view=True, records=records, selected_date=selected_date
    )


@admin_bp.route('/leave-requests')
def leave_requests():
    status_filter = request.args.get('status', 'Pending')
    query = Leave.query.join(Employee, Leave.employee_id == Employee.id)
    if status_filter != 'All':
        query = query.filter(Leave.status == status_filter)
    records = query.order_by(Leave.applied_at.desc()).all()
    return render_template(
        'leave.html', admin_view=True, records=records, status_filter=status_filter
    )


@admin_bp.route('/leave-requests/<int:leave_id>/review', methods=['POST'])
def review_leave(leave_id):
    leave = Leave.query.get_or_404(leave_id)
    action = request.form.get('action')
    comment = request.form.get('admin_comment', '').strip()

    if action not in ('Approved', 'Rejected'):
        flash('Invalid action.', 'danger')
        return redirect(url_for('admin.leave_requests'))

    leave.status = action
    leave.admin_comment = comment
    leave.reviewed_at = datetime.utcnow()

    _notify(
        leave.employee.user_id,
        f'Your {leave.leave_type} leave request ({leave.from_date} to {leave.to_date}) was {action.lower()}.'
    )
    db.session.commit()

    flash(f'Leave request {action.lower()}.', 'success')
    return redirect(url_for('admin.leave_requests'))


@admin_bp.route('/payroll')
def payroll_all():
    employees = Employee.query.order_by(Employee.first_name).all()
    pay_month = request.args.get('month', type=int) or date.today().month
    pay_year = request.args.get('year', type=int) or date.today().year

    records = Payroll.query.filter_by(pay_month=pay_month, pay_year=pay_year).all()
    records_by_emp = {r.employee_id: r for r in records}

    return render_template(
        'payroll.html',
        is_admin=True,
        employees=employees,
        records_by_emp=records_by_emp,
        pay_month=pay_month,
        pay_year=pay_year,
    )


@admin_bp.route('/payroll/update', methods=['POST'])
def payroll_update():
    employee_id = request.form.get('employee_id', type=int)
    pay_month = request.form.get('pay_month', type=int)
    pay_year = request.form.get('pay_year', type=int)

    employee = Employee.query.get(employee_id)
    if not employee or not pay_month or not pay_year:
        flash('Invalid employee or pay period.', 'danger')
        return redirect(url_for('admin.payroll_all'))

    try:
        basic_salary = float(request.form.get('basic_salary', 0))
        allowances = float(request.form.get('allowances', 0))
        deductions = float(request.form.get('deductions', 0))
    except (TypeError, ValueError):
        flash('Please enter valid numeric salary values.', 'danger')
        return redirect(url_for('admin.payroll_all', month=pay_month, year=pay_year))

    if basic_salary < 0 or allowances < 0 or deductions < 0:
        flash('Salary values cannot be negative.', 'danger')
        return redirect(url_for('admin.payroll_all', month=pay_month, year=pay_year))

    record = Payroll.query.filter_by(
        employee_id=employee_id, pay_month=pay_month, pay_year=pay_year
    ).first()
    if not record:
        record = Payroll(employee_id=employee_id, pay_month=pay_month, pay_year=pay_year)
        db.session.add(record)

    record.basic_salary = basic_salary
    record.allowances = allowances
    record.deductions = deductions
    record.calculate_net()

    _notify(employee.user_id, f'Your payroll for {pay_month}/{pay_year} has been updated.')
    db.session.commit()

    flash('Payroll updated successfully.', 'success')
    return redirect(url_for('admin.payroll_all', month=pay_month, year=pay_year))


@admin_bp.route('/analytics')
def analytics():
    return render_template('admin_dashboard.html', view='analytics')


# ---- JSON endpoints feeding the Chart.js charts on the analytics page ----

@admin_bp.route('/api/analytics/attendance')
def api_attendance_chart():
    today = date.today()
    total_employees = Employee.query.count() or 1

    labels, data = [], []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        labels.append(d.strftime('%b %d'))
        present_count = Attendance.query.filter_by(date=d, status='Present').count()
        data.append(round((present_count / total_employees) * 100, 1))

    return jsonify({'labels': labels, 'data': data})


@admin_bp.route('/api/analytics/leave')
def api_leave_chart():
    approved = Leave.query.filter_by(status='Approved').count()
    rejected = Leave.query.filter_by(status='Rejected').count()
    pending = Leave.query.filter_by(status='Pending').count()
    return jsonify({'labels': ['Approved', 'Rejected', 'Pending'], 'data': [approved, rejected, pending]})


@admin_bp.route('/api/analytics/departments')
def api_department_chart():
    results = (
        db.session.query(Employee.department, db.func.count(Employee.id))
        .group_by(Employee.department)
        .all()
    )
    labels = [r[0] or 'Unassigned' for r in results]
    data = [r[1] for r in results]
    return jsonify({'labels': labels, 'data': data})
