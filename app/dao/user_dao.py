from datetime import datetime

from sqlalchemy import or_

from app.dao.base_dao import BaseDao
from app.extension import db
from app.models import User
from config.logging import logger


class UserDao(BaseDao):
    """Handles direct database operations"""

    def paginate(filters, page: int, per_page: int):
        query = User.query.filter(User.deleted_at.is_(None))

        name = (filters.get("name") or "").strip()
        email = (filters.get("email") or "").strip()

        if name or email:
            or_conditions = []
            if name:
                or_conditions.append(User.name.ilike(f"%{name}%"))
            if email:
                or_conditions.append(User.email.ilike(f"%{email}%"))
            query = query.filter(or_(*or_conditions))

        # --- ROLE FILTER ---
        if filters.get("role") is not None:
            query = query.filter(User.role == filters["role"])

        # --- DATE FILTER ---
        start_date = filters.get("start_date")
        end_date = filters.get("end_date")
        try:
            if start_date:
                start = datetime.fromisoformat(start_date)
                query = query.filter(User.created_at >= start)

            if end_date:
                end = datetime.fromisoformat(end_date)
                query = query.filter(User.created_at <= end)

        except ValueError as e:
            logger.error(f"Invalid date format: {e}")

        # --- ORDER & PAGINATE ---
        return query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    def find_by_email(email: str):
        return User.query.filter_by(email=email, deleted_at=None).first()

    def is_valid_user(email: str):
        return User.query.filter_by(
            email=email, deleted_at=None, lock_flg=False
        ).first()

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

    def delete_users(user_ids: list[int]):
        """_Delete users_

        Args:
            user_ids (list[int]): _users ids_

        Returns:
            _list[int]_: _Deleted Users_
        """
        users = User.query.filter(
            User.id.in_(user_ids), User.deleted_at.is_(None)
        ).all()
        for user in users:
            user.soft_delete()
        db.session.commit()
        return users

    def lock_users(user_ids: list[int]):
        """_ Lock multiple users by updating lock_flg, lock_count, last_lock_at_

        Args:
            user_ids (list[int]): _users ids_

        Returns:
            _list[int]_: _locked users_
        """
        users = User.query.filter(
            User.id.in_(user_ids), User.deleted_at.is_(None)
        ).all()
        for user in users:
            user.lock_flg = True
            user.lock_count = (user.lock_count or 0) + 1
            user.last_lock_at = datetime.utcnow()
        db.session.commit()
        return users

    def unlock_users(user_ids: list[int]):
        """_ unLock multiple users by updating lock_flg, last_lock_at_

        Args:
            user_ids (list[int]): _users ids_

        Returns:
            _list[int]_: _unlocked users_
        """
        users = User.query.filter(
            User.id.in_(user_ids), User.deleted_at.is_(None)
        ).all()
        for user in users:
            user.lock_flg = False
            user.last_lock_at = None
        db.session.commit()
        return users
