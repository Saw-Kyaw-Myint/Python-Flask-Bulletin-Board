# app/exceptions/handler.py
from flask import jsonify
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from config.logging import logger  # or your global logger


def register_error_handlers(app):
    """
    Register global error handlers for the Flask application.

    This function sets up centralized handling for common exceptions,
    including Pydantic validation errors, HTTP 404 errors, database errors,
    and any unhandled exceptions. Each handler logs the error and returns
    a standardized JSON response with an appropriate HTTP status code.

    Handlers:
        1. ValidationError (Pydantic):
            - Logs a warning with detailed validation errors.
            - Returns 400 Bad Request with structured error information.

        2. 404 Not Found:
            - Logs a warning.
            - Returns 404 Not Found with a JSON message.

        3. SQLAlchemyError (Database errors):
            - Logs the error as an error.
            - Returns 500 Internal Server Error with a JSON message.

        4. Exception (Unhandled errors):
            - Logs the full exception.
            - Returns 500 Internal Server Error with a generic JSON message.

    Args:
        app (Flask): The Flask application instance to register handlers on.

    Returns:
        None
    """

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        """Handle Pydantic validation errors."""
        logger.warning(f"Validation Error: {e.errors()}")
        errors = [
            {
                "input": err.get("input", None),
                "loc": err.get("loc", []),
                "msg": err.get("msg", ""),
                "type": err.get("type", ""),
            }
            for err in e.errors()
        ]
        return jsonify(errors), 400

    @app.errorhandler(404)
    def handle_not_found(e):
        """Handle 404 Not Found errors."""
        logger.warning(f"404 Not Found: {e}")
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(e):
        """Handle database-related errors."""
        logger.error(f"Database Error: {str(e)}")
        return jsonify({"error": "Database error"}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        """Handle all other unhandled exceptions."""
        logger.error(f"Unhandled Exception: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
