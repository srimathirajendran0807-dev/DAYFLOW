"""
DAYFLOW - Authentication routes.

Handles registration, login, logout, and redirecting a logged-in user to
the correct dashboard for their role.
"""

from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from models import db
from models.user import User
from models.employee import Employee

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard_redirect'))

    if request.method == 'POST':
        employee_id = request.form.get('employee_id', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'employee')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()

        errors = []
        if not employee_id or not email or not password or not first_name or not last_name:
            errors.append('All fields are required.')
        if '@' not in email or '.' not in email.split('@')[-1]:
            errors.append('Please enter a valid email address.')
        if password != confirm_password:
            errors.append('Passwords do not match.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        if role not in ('employee', 'admin'):
            errors.append('Invalid role selected.')
        if not errors:
            if User.query.filter_by(email=email).first():
                errors.append('This email is already registered.')
            if User.query.filter_by(employee_id=employee_id).first():
                errors.append('This Employee ID is already in use.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('register.html', form=request.form)

        try:
            user = User(employee_id=employee_id, email=email, role=role, email_verified=True)
            user.set_password(password)
            db.session.add(user)
            db.session.flush()  # get user.id before commit

            employee = Employee(
                user_id=user.id,
                employee_id=employee_id,
                first_name=first_name,
                last_name=last_name,
                joining_date=datetime.utcnow().date()
            )
            db.session.add(employee)
            db.session.commit()

            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception:
            db.session.rollback()
            flash('Something went wrong while registering. Please try again.', 'danger')
            return render_template('register.html', form=request.form)

    return render_template('register.html', form={})


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard_redirect'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.employee.first_name if user.employee else user.email}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('auth.dashboard_redirect'))

        flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@auth_bp.route('/dashboard-redirect')
@login_required
def dashboard_redirect():
    if current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('employee.dashboard'))


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
