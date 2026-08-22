"""
DAYFLOW - Application configuration.

Database credentials and secrets are read from environment variables so that
no real credentials are ever hard-coded into source control. Sensible local
defaults are provided so the app also runs out-of-the-box for development.
"""

import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # --- Core Flask ---
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # --- Database ---
    # By default DAYFLOW runs against a bundled SQLite file (dayflow.db) so it
    # works immediately with zero external setup -- this avoids the
    # OperationalError that happens when MySQL isn't installed/running, the
    # database hasn't been created yet, or the credentials are wrong.
    #
    # To use real MySQL instead (as the spec calls for in production), either:
    #   1) set DATABASE_URL directly, e.g.
    #      mysql+pymysql://root:yourpassword@localhost:3306/dayflow_db
    #   2) or set USE_MYSQL=1 plus DB_USER / DB_PASSWORD / DB_HOST / DB_PORT / DB_NAME
    USE_MYSQL = os.environ.get('USE_MYSQL', '0') == '1'

    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'dayflow_db')

    if os.environ.get('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    elif USE_MYSQL:
        SQLALCHEMY_DATABASE_URI = (
            f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        )
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'dayflow.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True}

    # --- Mail (used for notification emails) ---
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@dayflow.com')
    MAIL_SUPPRESS_SEND = os.environ.get('MAIL_SUPPRESS_SEND', '1') == '1'

    # --- Uploads ---
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
