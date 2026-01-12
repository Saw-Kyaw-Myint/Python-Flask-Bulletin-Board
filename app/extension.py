"""
app/extension.py

This module initializes all Flask extensions used throughout the application.
It allows for centralized setup and supports the Flask app factory pattern.

Extensions:
    - db (SQLAlchemy): ORM for database interactions.
    - migrate (Migrate): Handles database migrations with Flask-Migrate.
    - ma (Marshmallow): Handles object serialization and deserialization.
    - limiter (Limiter): Implements rate limiting on routes, using the client IP
      as the key function.

Usage:
    from app.extension import db, migrate, ma, limiter

    def create_app():
        app = Flask(__name__)
        db.init_app(app)
        migrate.init_app(app, db)
        ma.init_app(app)
        limiter.init_app(app)
        return app
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.shared.database import softDelete, timeStamp

# Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
limiter = Limiter(key_func=get_remote_address)

db.timeStamp = timeStamp
db.softDelete = softDelete
