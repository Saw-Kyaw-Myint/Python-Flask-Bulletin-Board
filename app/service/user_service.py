from app.dao.user_dao import UserDao
from app.models import User
from app.service.base_service import BaseService


class UserService(BaseService):
    """Handles business logic"""

    def list():
        return UserDao.get_all()

    def create(payload):
        # Check unique email
        if UserDao.get_by_email(payload.email):
            raise ValueError("Email already exists")

        user = User(name=payload.name, email=payload.email)
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
