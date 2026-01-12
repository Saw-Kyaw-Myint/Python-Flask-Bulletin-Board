from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    jwt_required,
)

from app.extension import db
from app.models import User
from app.schema.user_schema import UserSchema
from config.logging import logger

user_schema = UserSchema(many=False)


def login_user():
    """
    Authenticate a user and return JWT access and refresh tokens.

    Expects a JSON payload in the request body with the following structure:
        {
            "email": "<user_email>"
        }

    Steps:
        1. Retrieve the user by email from the database.
        2. If the user does not exist, return a 404 error.
        3. Serialize the user data using UserSchema.
        4. Create JWT access and refresh tokens with user data as additional claims.
        5. Return the tokens as a JSON response.

    Returns:
        Response (JSON):
            - 200 OK with access_token and refresh_token if successful
            - 404 Not Found if user does not exist
    """
    json_data = request.json
    email = json_data.get("email")
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    # Dump user data to dict
    user_data = user_schema.dump(user)

    # Create access token with user info as additional claims
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
