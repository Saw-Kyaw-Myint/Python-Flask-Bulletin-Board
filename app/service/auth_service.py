import secrets
from datetime import datetime, timezone

from flask_bcrypt import Bcrypt, check_password_hash

from app.dao.password_reset_dao import PasswordResetDao
from app.dao.user_dao import UserDao
from app.service.base_service import BaseService
from app.shared.commons import field_error
from app.utils.hash import hash_password
from app.models.user import User

class AuthService(BaseService):
    def register(payload):
        """Register"""
        if UserDao.find_one(name=payload.name):
            field_error("name", "Name already exists", 400)

        if UserDao.find_one(email=payload.email):
            field_error("email", "Email already exists", 400)

        user = User(
            name=payload.name,
            email=payload.email,
            password=hash_password(payload.password),
        )
        user = UserDao.create(user)

        return {"user": user}

    def login(payload):
        """Login and update last_login_at"""
        user = UserDao.is_valid_user(payload.email)
        if not user:
            field_error("email", "The Email address doesn't exist.", 400)
        if not check_password_hash(user.password, payload.password):
            field_error("password", "Invalid credentials.", 400)
        user.last_login_at = datetime.now(timezone.utc)

        return user

    def forgot_password(payload):
        """Remove Token and insert token to DB"""
        user = UserDao.is_valid_user(payload.email)
        if not user:
            field_error(
                "email", "The Selected Email address doesn't exist or invalid.", 400
            )
        token = secrets.token_urlsafe(16)
        reset = PasswordResetDao.find_one(email=payload.email)
        if reset:
            reset.soft_delete()
        PasswordResetDao.create_password_reset(payload, token)

        return token

    def reset_password(payload):
        """
        Reset Password and remove token
        """
        reset = PasswordResetDao.find_one(token=payload.token)
        if not reset:
            field_error("token", "Invalid token", 400)
        user = UserDao.find_one(email=reset.email)
        user.password = hash_password(payload.password)
        reset.soft_delete()

        return user
