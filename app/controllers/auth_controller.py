from datetime import datetime, timedelta

from flask import jsonify, request, url_for
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from werkzeug.exceptions import HTTPException

from app.extension import db, limiter
from app.mail.reset_password_mail import ResetPasswordMail
from app.models import User
from app.request.auth_request import LoginRequest
from app.request.forgot_password import ForgotPasswordRequest
from app.request.register_request import RegisterRequest
from app.request.reset_password_request import RestPasswordRequest
from app.schema.auth_schema import AuthSchema
from app.service.auth_service import AuthService
from app.service.user_service import UserService
from app.shared.commons import FRONTEND_URL, validate_request
from app.utils.log import log_handler
from app.utils.token import (
    is_refresh_token_revoked,
    revoke_refresh_token,
    save_refresh_token,
)
from config.jwt import JWTConfig
from config.logging import logger

auth_schema = AuthSchema()

def hla():
    return('hls')

@validate_request(RegisterRequest)
def register(payload):
    try:
        user = AuthService.register(payload)
        db.session.commit()
        return jsonify({"msg": "Register is created successfully."}), 200
    except HTTPException as e:
        db.session.rollback()
        return e
    except Exception as e:
        db.session.rollback()
        log_handler("error", "User Controller : create_user =>", e)
        return jsonify({"msg": str(e)}), 500


@validate_request(LoginRequest)
def login_user(payload):
    """Authenticate a user and return JWT access and refresh tokens."""
    try:
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
    except HTTPException as e:
        db.session.rollback()
        return e
    except Exception as e:
        log_handler("error", "Auth Controller : login_user =>", e)
        db.session.rollback()
        return jsonify({"msg": str(e)}), 500


@jwt_required(refresh=True)
def refresh():
    """Generate Refresh token and Access Token"""
    try:
        claims = get_jwt()
        old_refresh_token = request.headers.get("X-refresh-token")
        user_id = get_jwt_identity()
        user = UserService.get_user(user_id)
        user_data = auth_schema.dump(user)
        if is_refresh_token_revoked(old_refresh_token):
            return {"msg": "Refresh token invalid."}, 403
        if not user:
            return {"msg": "Invalid identity."}, 403
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
        log_handler("error", "Auth Controller : refresh =>", e)
        db.session.rollback()
        return jsonify({"msg": str(e)}), 500


# @jwt_required()
# def get_me():
#     """
#     Retrieve the currently authenticated user's information.
#     """
#     claims = get_jwt()
#     user_info = claims.get("user")  # get full user dict
#     return jsonify({"user": user_info}), 200


@jwt_required()
def logout():
    """Logout"""
    try:
        old_refresh_token = request.headers.get("X-refresh-token")
        revoke_refresh_token(old_refresh_token)
        resp = jsonify({"msg": "Logout is success"})
        db.session.commit()

        return resp, 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": str(e)}), 500


def generate_and_save_refresh_token(
    user_id,
    isRememberMe,
):
    """
    Action to generate refresh token and access token
    """
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


@validate_request(ForgotPasswordRequest)
@limiter.limit("3 per minute")
def forgot_password(payload):
    """
    Send Reset password Mail with token
    """
    try:
        token = AuthService.forgot_password(payload)
        reset_url = f"{FRONTEND_URL}/reset-password?token={token}"
        ResetPasswordMail.send_reset_email(payload.email, reset_url)
        db.session.commit()
        return (
            jsonify({"msg": f"Password reset link has been sent to {payload.email}"}),
            200,
        )
    except HTTPException as e:
        db.session.rollback()
        return e
    except Exception as e:
        log_handler("error", "Auth Controller : forgot password =>", e)
        return jsonify({"msg": str(e)}), 500


@validate_request(RestPasswordRequest)
def reset_password(payload):
    try:
        AuthService.reset_password(payload)
        db.session.commit()
        return jsonify({"msg": "Password has been reset successfully"}), 200
    except HTTPException as e:
        db.session.rollback()
        return e
    except Exception as e:
        db.session.rollback()
        log_handler("error", "Auth Controller : reset password =>", e)
        return jsonify({"msg": str(e)}), 500
