from app.dao.user_dao import UserDao
from app.models import User
from app.service.base_service import BaseService
from app.shared.commons import field_error
from app.utils.hash import hash_password
from config.logging import logger


class UserService(BaseService):
    """Handles business logic"""

    def list():
        return UserDao.get_all()

    def create(payload):
        # Check unique email
        if UserDao.get_by_name(payload['name']):
            field_error('name',"Name already exists",401)
        
        if UserDao.get_by_email(payload['email']):
            field_error('email',"Email already exists",401)

        user = User(
            name=payload['name'],
            email=payload['email'],
            password=hash_password(payload['password']),
            role=payload['role'],
            phone=payload['phone'],
            dob=payload['dob'],
            address=payload['address'],
            profile_path=payload['profile'],
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
