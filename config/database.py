"""
config/database.py

Database configuration for the Flask application.

This module loads environment variables from a .env file and defines
the DatabaseConfig class, which centralizes database connection
settings and Flask SQLAlchemy configuration.

Environment Variables:
    - SECRET_KEY: Secret key for the Flask app. Defaults to 'dev_secret'.
    - DB_USER: Database username. Defaults to 'root'.
    - DB_PASSWORD: Database password. Defaults to 'root'.
    - DB_HOST: Database host. Defaults to 'localhost'.
    - DB_PORT: Database port. Defaults to '3306'.
    - DB_NAME: Database name. Defaults to 'flask_db'.

DatabaseConfig Class Attributes:
    - SECRET_KEY (str): Flask secret key.
    - DB_USER (str): Database username.
    - DB_PASSWORD (str): Database password.
    - DB_HOST (str): Database host.
    - DB_PORT (str): Database port.
    - DB_NAME (str): Database name.
    - SQLALCHEMY_DATABASE_URI (str): SQLAlchemy connection URI.
    - SQLALCHEMY_TRACK_MODIFICATIONS (bool): Disable Flask-SQLAlchemy event notifications.

Usage:
    from config.database import DatabaseConfig

    app.config.from_object(DatabaseConfig)
"""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class DatabaseConfig:
    """
    Centralized database configuration for Flask and SQLAlchemy.
    """

    # Secret key
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret")

    # MySQL connection parameters
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "flask_db")

    # SQLAlchemy connection URI
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Disable track modifications to save resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False
