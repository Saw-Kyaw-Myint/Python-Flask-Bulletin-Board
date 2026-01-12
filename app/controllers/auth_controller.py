from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    jwt_required,
)

from app.extension import db
from app.models import User
from app.request.auth_request import LoginRequest
from app.schema.user_schema import UserSchema
from app.service.auth_service import AuthService
from app.shared.commons import validate_request
from config.logging import logger

user_schema = UserSchema(many=False)


@validate_request(LoginRequest)
def login_user(payload):
    """
    Authenticate a user and return JWT access and refresh tokens.
    """

    try:
        user = AuthService.login(payload)
    except ValueError as e:
        return jsonify({"msg": str(e)}), 401

    user_data = user_schema.dump(user)
    access_token = create_access_token(
        identity=str(user.id), additional_claims={"user": user_data}
    )
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({"access_token": access_token, "refresh_token": refresh_token}), 200


@jwt_required()
def get_me():
    """
    Retrieve the currently authenticated user's information.

    This endpoint requires a valid JWT access token. It extracts the user
    information stored in the JWT claims and returns it.

    Steps:
        1. Verify JWT token using @jwt_required().
        2. Extract the user claims from the JWT.
        3. Return the full user dictionary as a JSON response.

    Returns:
        Response (JSON):
            - 200 OK with "user" key containing the current user's data
    """
    logger.info("hla")
    claims = get_jwt()
    user_info = claims.get("user")  # get full user dict
    return jsonify({"user": user_info}), 200
