# DAYFLOW – Human Resource Management System

*"Every workday, perfectly aligned."*

## Description

DAYFLOW is a centralized web-based HR Management System built as a college-level
software project. It digitizes core HR workflows for a small-to-medium
organization: employee onboarding, profile management, attendance tracking,
leave management, payroll visibility, HR/Admin approval workflows,
notifications, and basic analytics/reporting.

The system supports two roles:

- **Employee** – manages their own profile, attendance, leave, and views their payroll.
- **Admin / HR Officer** – manages all employees, reviews attendance, approves/rejects
  leave, maintains payroll, and views analytics/reports.

## Features

- Secure registration & login (hashed passwords, Flask-Login sessions)
- Role-based access control (Employee vs Admin, enforced on every route)
- Employee dashboard: profile, today's attendance, leave summary, salary, notifications
- Admin dashboard: employee counts, present/absent/on-leave today, pending leave requests
- Employee directory with admin edit capability
- Check-in / check-out attendance system with working-hour calculation
  - Prevents duplicate check-ins per day
  - Prevents check-out without check-in
- Leave application & approval workflow (Paid / Sick / Unpaid, Pending / Approved / Rejected)
  - Admin comments on decisions, visible instantly to the employee
- Read-only employee payroll view; full payroll management for Admin
  (net salary = basic + allowances − deductions, always server-calculated)
- In-app notifications for leave decisions and payroll updates
- HR Analytics: attendance %, leave statistics, employee count by department (Chart.js)
- Responsive Bootstrap 5 UI (desktop, tablet, mobile)
- Server-side validation everywhere; no raw Python/SQL errors shown to users

## Technologies

**Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript, Chart.js
**Backend:** Python 3, Flask, Flask-SQLAlchemy, Flask-Login, Flask-Mail, Werkzeug
**Database:** MySQL (via PyMySQL) in production, with a zero-config SQLite fallback for local development (see below)

## Project Structure

```
DAYFLOW/
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── .gitignore
├── models/          (User, Employee, Attendance, Leave, Payroll, Notification)
├── routes/          (auth, employee, attendance, leave, admin blueprints)
├── templates/       (Jinja2 HTML templates)
├── static/          (css, js, uploads)
└── database/        (dayflow.sql schema)
```

## Quick Start (no MySQL required)

By default DAYFLOW runs against a bundled SQLite file (`dayflow.db`, created
automatically the first time you run the app) so you can try it immediately
with nothing else to install or configure.

### 1. Install Python
Install Python 3.10+ from https://www.python.org/downloads/

### 2. Create a virtual environment
```bash
python -m venv venv
```

### 3. Activate it

Windows:
```bash
venv\Scripts\activate
```

macOS / Linux:
```bash
source venv/bin/activate
```

### 4. Install requirements
```bash
pip install -r requirements.txt
```

### 5. Run it
```bash
python app.py
```

On first run the app automatically creates all tables and the two demo
accounts below. Open your browser at **http://127.0.0.1:5000**

| Role     | Email                  | Password     |
|----------|-------------------------|--------------|
| Admin    | admin@dayflow.com        | Admin@123    |
| Employee | employee@dayflow.com     | Employee@123 |

**Never use these credentials in a real deployment** — change or delete them.

---

## Switching to MySQL (production setup)

The app is written for MySQL and switches to it automatically once you point
it there — nothing in the code needs to change.

### 1. Install MySQL
Install MySQL Server (8.x recommended) from https://dev.mysql.com/downloads/ and make sure the MySQL service is running.

### 2. Create the database
```sql
CREATE DATABASE dayflow_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Set the environment variables
```bash
set USE_MYSQL=1
set DB_USER=root
set DB_PASSWORD=your_mysql_password
set DB_HOST=localhost
set DB_PORT=3306
set DB_NAME=dayflow_db
set SECRET_KEY=some-long-random-string
```
(use `export` instead of `set` on macOS/Linux)

Alternatively, set a single `DATABASE_URL`, e.g.
`mysql+pymysql://root:yourpassword@localhost:3306/dayflow_db` — this takes priority over the individual `DB_*` variables.

### 4. Run it
```bash
python app.py
```
Tables and demo accounts are created automatically on startup here too — you do **not** need to separately import `database/dayflow.sql` (it's provided for reference/manual import if you prefer that route instead).

### Troubleshooting "OperationalError"
This means Flask-SQLAlchemy couldn't reach the database. Check that:
1. MySQL server is actually running.
2. The database named in `DB_NAME` (default `dayflow_db`) already exists — MySQL won't auto-create it.
3. `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` are correct for your MySQL install.
4. `USE_MYSQL=1` (or `DATABASE_URL`) is actually set in the same terminal session you run `python app.py` from.

Or simplest of all: unset those variables and let it fall back to SQLite.

## Demo Accounts

| Role     | Email                  | Password     |
|----------|-------------------------|--------------|
| Admin    | admin@dayflow.com        | Admin@123    |
| Employee | employee@dayflow.com     | Employee@123 |

To change these, either edit the `seed_demo()` function in `app.py` before running
`flask --app app seed-demo`, or log in and update the account directly.

## Functional Rules Enforced

1. Employees can only see their own attendance, leave, and salary records.
2. Employees cannot approve leave or access any Admin route.
3. Admins can view/manage all employees, attendance, leave, and payroll.
4. Employee payroll pages are strictly read-only.
5. A user cannot check in twice on the same date (enforced in code + DB unique constraint).
6. A user cannot check out before checking in.
7. Leave status changes appear to the employee immediately (same database record).
8. Leave approval/rejection and payroll updates generate notifications.

## Testing the Full Flow

**Employee:** Register → Login → Dashboard → Profile → Check In → Check Out →
Attendance → Apply Leave → View Leave Status → View Payroll → Logout

**Admin:** Login → Dashboard → View Employees → View Attendance → View Leave
Requests → Approve/Reject → Add Comment → Update Payroll → View Analytics → Logout
