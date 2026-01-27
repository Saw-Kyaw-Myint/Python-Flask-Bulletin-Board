from datetime import datetime
from itertools import batched

from flask_jwt_extended import get_jwt_identity
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from app.dao.base_dao import BaseDao
from app.extension import db
from app.models import User
from app.models.scopes import UserScopes
from app.shared.commons import BATCH_SIZE
from config.logging import logger


class UserDao(BaseDao):
    """Handles direct database operations"""

    def find_one(include_deleted: bool = False, **filters):
        """
        To Search specific column
        """
        query = User.query

        if not include_deleted:
            query = query.filter(User.deleted_at.is_(None))

        return query.filter_by(**filters).first()

    def is_valid_user(email: str):
        """
        Check unLock user
        """
        return User.query.filter_by(
            email=email, deleted_at=None, lock_flg=False
        ).first()

    def paginate(filters, page: int, per_page: int):
        """
        Paginate User records with optional filters for name, email, role, and creation date.
        """
        user_id = get_jwt_identity()
        query = User.query

        # --- Apply scopes from UserScopes ---
        query = UserScopes.active(query, exclude_user_id=user_id)
        query = UserScopes.filter_name_email(query, filters)
        query = UserScopes.filter_role(query, filters)
        query = UserScopes.filter_date(query, filters)

        return query.order_by(User.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    def create(user: User):
        """
        Create User
        """
        db.session.add(user)
        return user

    def get_user(user_id: int):
        """
        Get User with relationship
        """
        return (
            User.query.options(joinedload(User.creator), joinedload(User.updater))
            .filter_by(id=user_id, deleted_at=None, lock_flg=False)
            .first()
        )

    def delete_users(user_ids: list[int]):
        """
        Soft delete users by user ids in batches
        """
        deleted_count = 0
        for batch in batched(user_ids, BATCH_SIZE):
            logger.info(batch)
            users = User.query.filter(
                User.id.in_(batch), User.deleted_at.is_(None)
            ).all()
            for user in users:
                user.soft_delete()
                deleted_count += 1
        return deleted_count

    def delete_all_users(exclude_ids: list[int]):
        """
        Delete all user or all except exclude_ids.
        """
        query = User.query.filter(User.deleted_at.is_(None))
        if exclude_ids:
            query = query.filter(~User.id.in_(exclude_ids))
        deleted_count = query.update(
            {"deleted_at": datetime.utcnow()}, synchronize_session=False
        )
        db.session.flush()
        return deleted_count

    def lock_users(user_ids: list[int]):
        """
        Lock multiple users by updating lock_flg, lock_count, last_lock_at_
        """
        users = User.query.filter(
            User.id.in_(user_ids), User.deleted_at.is_(None)
        ).all()
        for user in users:
            user.lock_flg = True
            user.lock_count = (user.lock_count or 0) + 1
            user.last_lock_at = datetime.utcnow()
        return users

    def unlock_users(user_ids: list[int]):
        """
        UnLock multiple users by updating lock_flg, last_lock_at_
        """
        users = User.query.filter(
            User.id.in_(user_ids), User.deleted_at.is_(None)
        ).all()
        for user in users:
            user.lock_flg = False
            user.last_lock_at = None
        return users
