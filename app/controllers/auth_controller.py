from datetime import datetime, timedelta

from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)

from app.extension import db
from app.models import User
from app.request.auth_request import LoginRequest
from app.schema.auth_schema import AuthSchema
from app.service.auth_service import AuthService
from app.service.user_service import UserService
from app.shared.commons import validate_request
from app.utils.token import (
    is_refresh_token_revoked,
    revoke_refresh_token,
    save_refresh_token,
)
from config.jwt import JWTConfig
from config.logging import logger

auth_schema = AuthSchema()


@validate_request(LoginRequest)
def login_user(payload):
    """
    Authenticate a user and return JWT access and refresh tokens.
    """
    user = AuthService.login(payload)
    user_data = auth_schema.dump(user)
    access_token = create_access_token(
        identity=str(user.id), additional_claims={"user": user_data}
    )
    remember_me = True if payload.remember else False
    refresh_token = generate_and_save_refresh_token(user.id, remember_me)
    response = jsonify(access_token=access_token, refresh_token=refresh_token)
    db.session.commit()

    return response, 200


@jwt_required(refresh=True)
def refresh():
    try:
        claims = get_jwt()
        old_refresh_token = request.headers.get("X-refresh-token")
        user_id = get_jwt_identity()
        user = UserService.get_user(user_id)
        user_data = auth_schema.dump(user)
        if is_refresh_token_revoked(old_refresh_token):
            return {"msg": "Refresh token invalid."}, 402

        if not user:
            return {"msg": "Invalid identity."}, 404
        revoke_refresh_token(old_refresh_token)
        new_access_token = create_access_token(
            identity=str(user_id), additional_claims={"user": user_data}
        )
        remember_me = bool(claims.get("remember_me", False))
        new_refresh_token = generate_and_save_refresh_token(user_id, remember_me)
        resp = jsonify(access_token=new_access_token, refresh_token=new_refresh_token)
        db.session.commit()

        return resp, 200
    except Exception as e:
        logger.error("Auth Controller : refresh")
        logger.error(e)
        db.session.rollback()
        return jsonify({"message": str(e)}), 409


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
    claims = get_jwt()
    user_info = claims.get("user")  # get full user dict
    return jsonify({"user": user_info}), 200


@jwt_required()
def logout():
    try:
        old_refresh_token = request.headers.get("X-refresh-token")
        revoke_refresh_token(old_refresh_token)
        resp = jsonify({"msg": "Logout is success"})

        return resp, 200
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 409


def generate_and_save_refresh_token(
    user_id,
    isRememberMe,
):
    if isRememberMe:
        expire_timedelta = timedelta(seconds=JWTConfig.JWT_REMEMBER_ME_EXPIRES)
        expires_at = datetime.utcnow() + expire_timedelta
        refresh_token = create_refresh_token(
            identity=str(user_id),
            expires_delta=expire_timedelta,
            additional_claims={"remember_me": True},
        )
    else:
        expire_delta = timedelta(seconds=JWTConfig.JWT_REFRESH_TOKEN_EXPIRES)
        expires_at = datetime.utcnow() + expire_delta
        refresh_token = create_refresh_token(
            identity=str(user_id),
            expires_delta=expire_delta,
        )

    save_refresh_token(user_id, refresh_token, expires_at)

    return refresh_token
