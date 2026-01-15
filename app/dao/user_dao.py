from app.dao.base_dao import BaseDao
from app.extension import db
from app.models import User


class UserDao(BaseDao):
    """Handles direct database operations"""

    def find_by_email(email: str):
        return User.query.filter_by(email=email, deleted_at=None).first()
    
    def update_last_login():
        return User.query.filter_by(email=email, deleted_at=None).first()

    def get_all():
        return User.query.all()

    def get_by_id(user_id: int):
        return User.query.get(user_id)

    def get_by_email(email: str):
        return User.query.filter_by(email=email).first()
    
    def get_by_name(name: str):
        return User.query.filter_by(name=name).first()

    def create(user: User):
        db.session.add(user)
        db.session.commit()
        return user

    def update():
        db.session.commit()

    def delete(user: User):
        user.soft_delete()
        db.session.commit()
