from datetime import datetime
from itertools import batched

from flask_jwt_extended import get_jwt_identity
from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from app.dao.base_dao import BaseDao
from app.extension import db
from app.models import User
from app.models.scopes import UserScopes
from app.shared.commons import BATCH_SIZE
from app.utils.request import clean_filters
from config.logging import logger


class UserDao(BaseDao):
    """Handles direct database operations"""

    def find_one(include_deleted: bool = False, **filters):
        """To Search specific column"""
        query = User.query
        if not include_deleted:
            query = UserScopes.active(query)
        return query.filter_by(**filters).first()

    def is_valid_user(email: str):
        """Check unLock user"""
        return User.query.filter_by(
            email=email, deleted_at=None, lock_flg=False
        ).first()

    def paginate(filters, page: int, per_page: int):
        """Paginate User records with optional filters for name, email, role, and creation date."""
        user_id = get_jwt_identity()
        query = User.query
        query = UserScopes.active(query, exclude_user_id=user_id)
        query = UserScopes.filter_name_email(query, filters)
        query = UserScopes.filter_role(query, filters)
        query = UserScopes.filter_date(query, filters)
        query = UserScopes.latest(query)

        return query.paginate(page=page, per_page=per_page, error_out=False)

    def create(user: User):
        """Create User"""
        db.session.add(user)
        return user

    def get_user(user_id: int):
        """Get User with relationship"""
        return (
            User.query.options(joinedload(User.creator), joinedload(User.updater))
            .filter_by(id=user_id, deleted_at=None, lock_flg=False)
            .first()
        )

    def delete_users(user_ids: list[int]):
        """Soft delete users by user ids in batches"""
        deleted_count = 0
        for batch in batched(user_ids, BATCH_SIZE):
            users = User.query.filter(
                User.id.in_(batch), User.deleted_at.is_(None)
            ).all()
            for user in users:
                user.soft_delete()
                deleted_count += 1
        return deleted_count

    def delete_all_users(exclude_ids: list[int], filters):
        """Delete all user or all except exclude_ids."""
        user_id = get_jwt_identity()
        query = User.query.filter(User.deleted_at.is_(None), User.id != user_id)
        if exclude_ids:
            query = query.filter(~User.id.in_(exclude_ids))
        if filters:
            filters = clean_filters(filters)
            query = UserDao.filters_query(query, filters, True, False)
        deleted_count = query.update(
            {"deleted_at": datetime.utcnow()}, synchronize_session=False
        )
        db.session.flush()
        return deleted_count

    def lock_all_users(exclude_ids: list[int], filters):
        """Lock all users or all except exclude_ids."""
        user_id = get_jwt_identity()
        query = User.query.filter(User.deleted_at.is_(None), User.id != user_id)
        if exclude_ids:
            query = query.filter(~User.id.in_(exclude_ids))
        if filters:
            filters = clean_filters(filters)
            query = UserDao.filters_query(query, filters, True, False)
        lock_count = query.update(
            {
                User.lock_flg: True,
                User.lock_count: func.coalesce(User.lock_count, 0) + 1,
                User.last_lock_at: datetime.utcnow(),
            },
            synchronize_session=False,
        )

        db.session.flush()
        return lock_count

    def lock_users(user_ids: list[int]):
        """Lock multiple users by updating lock_flg, lock_count, last_lock_at"""
        users = User.query.filter(
            User.id.in_(user_ids), User.deleted_at.is_(None)
        ).all()
        for user in users:
            user.lock_flg = True
            user.lock_count = (user.lock_count or 0) + 1
            user.last_lock_at = datetime.utcnow()
        return users

    def unlock_all_users(exclude_ids: list[int], filters):
        """Lock all users or all except exclude_ids."""
        query = User.query.filter(User.deleted_at.is_(None))
        if exclude_ids:
            query = query.filter(~User.id.in_(exclude_ids))
        if filters:
            filters = clean_filters(filters)
            query = UserDao.filters_query(query, filters, True, False)
        lock_count = query.update(
            {
                User.lock_flg: False,
                User.last_lock_at: datetime.utcnow(),
            },
            synchronize_session=False,
        )

        db.session.flush()
        return lock_count

    def unlock_users(user_ids: list[int]):
        """UnLock multiple users by updating lock_flg, last_lock_at"""
        users = User.query.filter(
            User.id.in_(user_ids), User.deleted_at.is_(None)
        ).all()
        for user in users:
            user.lock_flg = False
            user.last_lock_at = None
        return users

    def filters_query(query, filters, active=True, latest=True, current_user_id=None):
        """Filter Query"""
        if active:
            query = UserScopes.active(query, exclude_user_id=current_user_id)
        query = UserScopes.filter_name_email(query, filters)
        query = UserScopes.filter_role(query, filters)
        query = UserScopes.filter_date(query, filters)
        if latest:
            query = UserScopes.latest(query)
        return query
