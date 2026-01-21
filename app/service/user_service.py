from app.dao.user_dao import UserDao
from app.models import User
from app.service.base_service import BaseService
from app.shared.commons import field_error
from app.utils.hash import hash_password
from config.logging import logger


class UserService(BaseService):
    """Handles business logic"""

    def filter_paginate(filters, page: int, per_page: int):
        users = UserDao.paginate(filters, page, per_page)
        return users

    def list():
        return UserDao.get_all()

    def get_user(user_id):
        user = UserDao.get_user(user_id)
        if not user:
            return ValueError("User don't not exist.")
        return user

    def create(payload):
        if UserDao.get_by_name(payload["name"]):
            field_error("name", "Name already exists", 402)

        if UserDao.get_by_email(payload["email"]):
            field_error("email", "Email already exists", 402)

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
        user = UserDao.get_by_id(id)
        if not user:
            field_error("internal_error", "Email  don't exists", 402)

        exist_name = UserDao.get_by_name(payload["name"])
        exist_email = UserDao.get_by_email(payload["email"])
        if exist_name and exist_name.name != user.name:
            field_error("name", "Name already exists", 402)

        if UserDao.get_by_email(payload["email"]) and exist_email.email != user.email:
            field_error("email", "Email already exists", 402)

        user.name = payload["name"]
        user.email = payload["email"]
        user.role = payload["role"]
        user.address = payload["address"]
        user.updated_user_id = payload["user_id"]

        if payload.get("password"):
            user.password = hash_password(payload["password"])

        if payload.get("profile"):
            user.profile_path = payload["profile"]
        return user

    def delete(user_id):
        user = UserDao.get_by_id(user_id)
        if not user:
            return False
        UserDao.delete(user)
        return True

    def delete_users(user_ids):
        """_Delete Users_

        Args:
            user_ids (_List[int]_): _user's ids_

        Raises:
            ValueError: _not user found_

        Returns:
            _list[int]_: _deleted users_
        """
        users = UserDao.delete_users(user_ids)
        if not users:
            raise ValueError("not user found")
        return users

    def lock_users(users_ids):
        """_Lock User_

        Args:
            users_ids (_list[int]_): _user's ids_

        Raises:
            ValueError: _not user found_

        Returns:
            _list[int]_: _lock users_
        """
        users = UserDao.lock_users(users_ids)
        if not users:
            raise ValueError("not user found")
        return users

    def unlock_users(users_ids):
        """_unLock User_

        Args:
            users_ids (_list[int]_): _user's ids_

        Raises:
            ValueError: _not user found_

        Returns:
            _list[int]_: _unlock users_
        """
        users = UserDao.unlock_users(users_ids)
        if not users:
            raise ValueError("not user found")
        return users
