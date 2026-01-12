"""
config/logging.py

Logging configuration for the Flask application.

This module sets up a global logger that writes log messages to a
rotating file and allows attaching it to a Flask app. It ensures
persistent logging with file rotation to avoid large log files.

Logger Configuration:
    - Base directory: Project root
    - Log directory: <BASE_DIR>/logging
    - Log file: app.log
    - Max file size: 5 MB
    - Backup count: 5
    - Log format: [timestamp] LEVEL in module: message
    - Log level: INFO

Usage:
    from config.logging import logger, setup_logging

    # Optional: attach logger to Flask app
    setup_logging(app)
"""

import logging
import os
from logging.handlers import RotatingFileHandler

# Set project root as base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logging")
os.makedirs(LOG_DIR, exist_ok=True)

# Create a global logger
logger = logging.getLogger("myapp_logger")
logger.setLevel(logging.INFO)

log_file = os.path.join(LOG_DIR, "app.log")
handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5)
formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def setup_logging(app):
    """
    Attach the global logger to a Flask application instance.

    This allows Flask's internal logging to use the same file handler
    and formatting as the global logger.

    Args:
        app (Flask): The Flask application instance.

    Returns:
        None
    """
    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)
