"""
config/jwt.py

JWT (JSON Web Token) configuration for the Flask application.

This module loads environment variables from a `.env` file and defines
the `JWTConfig` class, which centralizes JWT-related settings such as
secret key and token expiration times.

Environment Variables:
    - JWT_SECRET_KEY: Secret key used to sign JWTs. Defaults to 'fallback_secret'.
    - JWT_ACCESS_TOKEN_EXPIRES: Expiration time for access tokens (in seconds). Defaults to 3600 (1 hour).
    - JWT_REFRESH_TOKEN_EXPIRES: Expiration time for refresh tokens (in seconds). Defaults to 86400 (24 hours).

JWTConfig Class Attributes:
    - JWT_SECRET_KEY (str): Secret key for signing JWTs.
    - JWT_ACCESS_TOKEN_EXPIRES (int): Access token expiration time in seconds.
    - JWT_REFRESH_TOKEN_EXPIRES (int): Refresh token expiration time in seconds.

Usage:
    from config.jwt import JWTConfig

    app.config.from_object(JWTConfig)
"""

import os

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class JWTConfig:
    """
    Centralized JWT configuration for Flask-JWT-Extended.
    """

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "fallback_secret")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 3600))
    JWT_REFRESH_TOKEN_EXPIRES = int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRES", 86400))
