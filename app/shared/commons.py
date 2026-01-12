from functools import wraps

from flask import jsonify, request
from pydantic import ValidationError


def validate_request(schema):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                payload = schema.model_validate(request.json)
            except ValidationError as e:
                return jsonify({"errors": format_pydantic_errors(e)}), 401

            return fn(payload, *args, **kwargs)

        return wrapper

    return decorator


def format_pydantic_errors(exc: ValidationError):
    """
    Format Pydantic validation errors into a simplified list of dictionaries.

    Each error is transformed into a dictionary with:
        - `field`: Dot-separated path of the invalid field.
        - `message`: Human-readable error message.

    Args:
        exc (ValidationError): The Pydantic validation error instance.

    Returns:
        List[dict]: A list of dictionaries representing the formatted errors.

    Example:
        [
            {"field": "user.email", "message": "value is not a valid email"},
            {"field": "user.age", "message": "ensure this value is greater than 0"}
        ]
    """
    formatted_errors = []
    for err in exc.errors():
        formatted_errors.append(
            {"field": ".".join(str(loc) for loc in err["loc"]), "message": err["msg"]}
        )
    return formatted_errors


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
