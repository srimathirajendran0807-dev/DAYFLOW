"""
DAYFLOW - Human Resource Management System
Main application entrypoint.

Run:
    python app.py

That's it -- no separate setup step is required. On startup the app:
  1) creates all database tables if they don't already exist, and
  2) seeds the two demo accounts (admin@dayflow.com / employee@dayflow.com)
     if they aren't already present.

By default this runs against a bundled SQLite file (dayflow.db) so it works
immediately with no external database to install or configure. To point it
at real MySQL instead, see the "Database" section in config.py / README.md.
"""

import sys

from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager, current_user
from flask_mail import Mail
from sqlalchemy.exc import OperationalError

from config import Config
from models import db
from models.user import User


def _seed_demo_accounts():
    """Create demo admin and employee accounts for testing (idempotent)."""
    from datetime import date
    from models.employee import Employee

    if not User.query.filter_by(email='admin@dayflow.com').first():
        admin_user = User(
            employee_id='ADM001', email='admin@dayflow.com',
            role='admin', email_verified=True
        )
        admin_user.set_password('Admin@123')
        db.session.add(admin_user)
        db.session.flush()
        db.session.add(Employee(
            user_id=admin_user.id, employee_id='ADM001',
            first_name='Admin', last_name='User',
            department='Human Resources', designation='HR Manager',
            joining_date=date.today()
        ))

    if not User.query.filter_by(email='employee@dayflow.com').first():
        emp_user = User(
            employee_id='EMP001', email='employee@dayflow.com',
            role='employee', email_verified=True
        )
        emp_user.set_password('Employee@123')
        db.session.add(emp_user)
        db.session.flush()
        db.session.add(Employee(
            user_id=emp_user.id, employee_id='EMP001',
            first_name='John', last_name='Doe',
            department='Engineering', designation='Software Developer',
            joining_date=date.today()
        ))

    db.session.commit()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Mail(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- Blueprints ---
    from routes.auth import auth_bp
    from routes.employee import employee_bp
    from routes.attendance import attendance_bp
    from routes.leave import leave_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(employee_bp, url_prefix='/employee')
    app.register_blueprint(attendance_bp, url_prefix='/attendance')
    app.register_blueprint(leave_bp, url_prefix='/leave')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('auth.dashboard_redirect'))
        return redirect(url_for('auth.login'))

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return render_template('500.html'), 500

    # --- CLI commands (still available if you prefer manual control) ---
    @app.cli.command('init-db')
    def init_db():
        """Create all database tables."""
        db.create_all()
        print('Database tables created.')

    @app.cli.command('seed-demo')
    def seed_demo():
        """Create demo admin and employee accounts for testing."""
        _seed_demo_accounts()
        print('Demo accounts ready: admin@dayflow.com / Admin@123, employee@dayflow.com / Employee@123')

    # --- Automatic setup on startup ---
    with app.app_context():
        try:
            db.create_all()
            _seed_demo_accounts()
        except OperationalError as exc:
            print('=' * 70)
            print('DAYFLOW could not connect to the database.')
            print('Details:', exc.orig if hasattr(exc, "orig") else exc)
            print()
            print('If you are trying to use MySQL, check that:')
            print('  1) MySQL server is actually running')
            print('  2) The database from DB_NAME (default "dayflow_db") exists')
            print('  3) DB_USER / DB_PASSWORD / DB_HOST / DB_PORT are correct')
            print('  4) USE_MYSQL=1 (or DATABASE_URL) is set in your environment')
            print()
            print('Or simply unset those variables to fall back to the bundled')
            print('SQLite database, which requires no setup at all.')
            print('=' * 70)
            sys.exit(1)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
