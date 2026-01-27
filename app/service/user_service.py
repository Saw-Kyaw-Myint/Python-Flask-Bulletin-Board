from flask_jwt_extended import get_jwt_identity

from app.dao.user_dao import UserDao
from app.models import User
from app.service.base_service import BaseService
from app.shared.commons import field_error
from app.utils.hash import hash_password
from config.logging import logger


class UserService(BaseService):
    """Handles business logic"""

    def filter_paginate(filters, page: int, per_page: int):
        """
        User List with pagination
        """
        users = UserDao.paginate(filters, page, per_page)
        return users

    def get_user(user_id):
        """
        Get User by User ID
        """
        user = UserDao.get_user(user_id)
        if not user:
            raise ValueError("User don't not exist.")
        return user

    def create(payload):
        """
        Create User
        """
        if UserDao.find_one(name=payload["name"]):
            field_error("name", "Name already exists", 400)

        if UserDao.find_one(email=payload["email"]):
            field_error("email", "Email already exists", 400)

        user = User(
            name=payload["name"],
            email=payload["email"],
            password=hash_password(payload["password"]),
            role=payload["role"],
            phone=payload["phone"],
            dob=payload["dob"],
            address=payload["address"],
            profile_path=payload["profile"],
            create_user_id=payload["user_id"],
        )

        return UserDao.create(user)

    def update(payload, id):
        """
        Update User
        """
        user = UserDao.find_one(id=id, include_deleted=False)
        if not user:
            field_error("internal_error", "Email  don't exists", 400)

        exist_name = UserDao.find_one(name=payload["name"])
        exist_email = UserDao.find_one(email=payload["email"])
        if exist_name and exist_name.name != user.name:
            field_error("name", "Name already exists", 400)

        if UserDao.find_one(email=payload["email"]) and exist_email.email != user.email:
            field_error("email", "Email already exists", 400)

        user.name = payload["name"]
        user.email = payload["email"]
        user.role = payload["role"]
        user.address = payload["address"]
        user.updated_user_id = get_jwt_identity()

        if payload.get("password"):
            user.password = hash_password(payload["password"])

        if payload.get("profile"):
            user.profile_path = payload["profile"]
        return user

    def delete_users(payload):
        """
        Delete Users
        """
        select_all = payload.get("all", False)
        user_ids = payload.get("user_ids", [])
        exclude_ids = payload.get("exclude_ids", [])
        if select_all:
            user_count = UserDao.delete_all_users(exclude_ids)
        else:
            if not isinstance(user_ids, list) or not user_ids:
                raise ValueError("Provide user ids list.")
            user_count = UserDao.delete_users(user_ids)
        return user_count

    def lock_users(users_ids):
        """
        Lock User
        """
        users = UserDao.lock_users(users_ids)
        if not users:
            raise ValueError("not user found")
        return users

    def unlock_users(users_ids):
        """
        UnLock User
        """
        users = UserDao.unlock_users(users_ids)
        if not users:
            raise ValueError("not user found")
        return users
