-- =====================================================================
-- DAYFLOW HRMS - Database Schema
-- Import with:  mysql -u root -p dayflow_db < database/dayflow.sql
-- (Note: `flask --app app init-db` will also create these tables for you
--  automatically from the SQLAlchemy models — you only need one or the
--  other, not both.)
-- =====================================================================

CREATE DATABASE IF NOT EXISTS dayflow_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE dayflow_db;

-- ---------------------------------------------------------------------
-- users
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'employee',
    email_verified BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- employees
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    employee_id VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    address VARCHAR(255),
    date_of_birth DATE,
    gender VARCHAR(10),
    department VARCHAR(50),
    designation VARCHAR(50),
    joining_date DATE,
    profile_picture VARCHAR(255) DEFAULT 'default.png',
    documents VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_employees_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- attendance
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    date DATE NOT NULL,
    check_in TIME,
    check_out TIME,
    working_hours FLOAT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'Present',
    CONSTRAINT fk_attendance_employee FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    CONSTRAINT uq_attendance_employee_date UNIQUE (employee_id, date)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- leaves
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS leaves (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    leave_type VARCHAR(20) NOT NULL,
    from_date DATE NOT NULL,
    to_date DATE NOT NULL,
    remarks VARCHAR(255),
    status VARCHAR(20) DEFAULT 'Pending',
    admin_comment VARCHAR(255),
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reviewed_at DATETIME,
    CONSTRAINT fk_leaves_employee FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- payroll
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS payroll (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    basic_salary FLOAT NOT NULL DEFAULT 0,
    allowances FLOAT DEFAULT 0,
    deductions FLOAT DEFAULT 0,
    net_salary FLOAT DEFAULT 0,
    pay_month INT NOT NULL,
    pay_year INT NOT NULL,
    salary_slip VARCHAR(255),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_payroll_employee FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    CONSTRAINT uq_payroll_employee_month_year UNIQUE (employee_id, pay_month, pay_year)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- notifications  (supports the Notifications feature, section 13)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message VARCHAR(255) NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notifications_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Demo accounts (optional).
-- Password hashes below correspond to plaintext passwords used ONLY for
-- local testing: Admin@123 and Employee@123. Do NOT use these in
-- production. Easiest: skip this section and instead run
--   flask --app app seed-demo
-- which creates the same two accounts through the application itself.
-- ---------------------------------------------------------------------
