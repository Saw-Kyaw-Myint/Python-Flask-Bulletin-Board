import os
from functools import wraps
from typing import Any

from flask import abort, jsonify, make_response, request
from flask.wrappers import Response
from marshmallow import Schema
from pydantic import ValidationError

from config.logging import logger

BATCH_SIZE = int(os.environ.get("BATCH_SIZE", 50))
FRONTEND_URL = os.environ.get("FRONTEND_URL")
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1 MB


def validate_request(schema):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()
            try:
                payload = schema.model_validate(data)
            except ValidationError as e:
                return jsonify({"errors": format_pydantic_errors(e, schema)}), 422

            return fn(payload, *args, **kwargs)

        return wrapper

    return decorator


def format_pydantic_errors(e, schema):
    errors = {}

    attributes = schema.attributes() if hasattr(schema, "attributes") else {}
    messages = schema.messages() if hasattr(schema, "messages") else {}

    for err in e.errors():
        field = err["loc"][-1]  # password
        rule = err["type"]  # string_too_short
        message_key = f"{field}.{rule}"  # password.string_too_short

        logger.info(message_key)

        # 1️⃣ custom message
        if message_key in messages:
            errors[field] = messages[message_key]
            continue

        # 2️⃣ default fallback
        label = attributes.get(field, field.capitalize())

        if rule == "missing":
            errors[field] = f"{label} is required"
        else:
            errors[field] = err["msg"]

    return errors


def before_middleware(bp, middleware):
    """
    Register a function to run **before each request** on a Flask blueprint.

    This is a helper wrapper around Flask's `before_request` decorator.

    Args:
        bp (Blueprint): The Flask Blueprint instance.
        middleware (Callable): A function to execute before each request.

    Returns:
        None
    """

    @bp.before_request
    def _middleware():
        return middleware()


def after_middleware(bp, middleware):
    """
    Register a function to run **after each request** on a Flask blueprint.

    This is a helper wrapper around Flask's `after_request` decorator.

    Args:
        bp (Blueprint): The Flask Blueprint instance.
        middleware (Callable): A function to execute after each request.
                               Must accept a response argument if needed.

    Returns:
        None
    """

    @bp.after_request
    def _middleware(response):
        # Pass the response to the middleware
        return middleware(response)


def field_error(field: str, message: str, status_code: int = 400):
    """
    Raise a JSON error for a specific field.

    :param field: Field name (e.g., 'email' or 'password')
    :param message: Error message
    :param status_code: HTTP status code
    """
    response = make_response(jsonify({"errors": {field: message}}), status_code)
    abort(response)


def raise_error(name: str, message: str, status_code: int = 400):
    """
    Raise a JSON error for a specific raise_error.

    :param raise_error: raise_error name (e.g., 'message' or 'message')
    :param message: Error message
    :param status_code: HTTP status code
    """
    response = make_response(jsonify({"errors": {name: message}}), status_code)
    abort(response)


def paginate_response(pagination: Any, schema: Schema) -> Response:
    """
    Return a standard JSON response for paginated data.
    """
    return jsonify(
        {
            "data": schema.dump(pagination.items),
            "meta": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages,
            },
        }
    )


def response_valid_request():
    return {"is_valid_request": True}
