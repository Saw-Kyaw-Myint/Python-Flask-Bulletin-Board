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

    def create(payload):
        # Check unique email
        if UserDao.get_by_name(payload["name"]):
            field_error("name", "Name already exists", 401)

        if UserDao.get_by_email(payload["email"]):
            field_error("email", "Email already exists", 401)

        user = User(
            name=payload["name"],
            email=payload["email"],
            password=hash_password(payload["password"]),
            role=payload["role"],
            phone=payload["phone"],
            dob=payload["dob"],
            address=payload["address"],
            profile_path=payload["profile"],
        )

        return UserDao.create(user)

    def update(user_id, payload):
        user = UserDao.get_by_id(user_id)
        if not user:
            return None

        if payload.email:
            exists = UserDao.get_by_email(payload.email)
            if exists and exists.id != user_id:
                raise ValueError("Email already exists")
            user.email = payload.email

        if payload.name:
            user.name = payload.name

        UserDao.update()
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
