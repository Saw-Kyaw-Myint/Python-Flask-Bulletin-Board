from flask import request
from flask_jwt_extended import verify_jwt_in_request

CONDITIONAL_JWT_ROUTES = [
    "/api/posts",
    "/api/posts/export/csv",
]


def post_middleware():
    """
    Placeholder middleware function for user-related request processing.

    This function is intended to be used as a middleware hook (before or
    after a request) in a Flask application. Currently, it does not perform
    any actions.

    Returns:
        None
    """
    path = request.path.rstrip("/")

    # Skip routes that don't need JWT at all
    if path not in CONDITIONAL_JWT_ROUTES:
        verify_jwt_in_request()
        return
    

        # Skip routes that don't need JWT at all
    if path not in CONDITIONAL_JWT_ROUTES:
        verify_jwt_in_request()
        return
        # Skip routes that don't need JWT at all
    if path not in CONDITIONAL_JWT_ROUTES:
        verify_jwt_in_request()
        return
    # If any filter param is provided, require JWT
    filter_params = ["name", "description", "status", "date"]
    if any(request.args.get(param) is not None for param in filter_params):
        verify_jwt_in_request()
