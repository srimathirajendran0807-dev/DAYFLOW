"""
DAYFLOW - models package.

`db` is created here (not in app.py) so every model file can import it
without circular-import problems.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
