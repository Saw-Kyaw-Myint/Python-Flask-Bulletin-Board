from datetime import datetime
from itertools import batched

from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from app.dao.base_dao import BaseDao
from app.extension import db
from app.models.post import Post
from app.shared.commons import BATCH_SIZE
from config.logging import logger


class PostDao(BaseDao):

    def paginate(filters, page: int, per_page: int):
        """
        Return filtered and paginated posts.
        """
        query = Post.query.filter(Post.deleted_at.is_(None))
        name = (filters.get("name") or "").strip()
        description = (filters.get("description") or "").strip()

        if name or description:
            or_conditions = []
            if name:
                or_conditions.append(Post.title.ilike(f"%{name}%"))
            if description:
                or_conditions.append(Post.description.ilike(f"%{description}%"))
            query = query.filter(or_(*or_conditions))

        # --- ROLE FILTER ---
        if filters.get("status") is not None:
            query = query.filter(Post.status == filters["status"])

        # --- DATE FILTER ---
        created_at = filters.get("date")

        try:
            if created_at:
                created_date = datetime.fromisoformat(created_at)
                query = query.filter(func.date(Post.created_at) == created_date)
        except ValueError as e:
            logger.error(f"Invalid date format: {e}")

        # --- ORDER & PAGINATE ---
        return query.order_by(Post.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    def create(post: Post):
        """
        Add post to session
        """
        db.session.add(post)
        return post

    def get_post(post_id: int):
        """
        Get Post using post id
        """ ""
        return (
            Post.query.options(joinedload(Post.creator), joinedload(Post.updater))
            .filter_by(id=post_id, deleted_at=None)
            .first()
        )

    def delete_posts(post_ids: list[int]):
        """
        Soft delete posts by post ids in batches
        """
        deleted_count = 0
        for batch in batched(post_ids, BATCH_SIZE):
            posts = Post.query.filter(
                Post.id.in_(batch), Post.deleted_at.is_(None)
            ).all()
            for post in posts:
                post.soft_delete()
                deleted_count += 1
        return deleted_count

    def delete_all_posts(exclude_ids):
        """
        Delete all posts or all except exclude_ids.
        """
        query = Post.query.filter(Post.deleted_at.is_(None))
        if exclude_ids:
            query = query.filter(~Post.id.in_(exclude_ids))
        deleted_count = query.update(
            {"deleted_at": datetime.utcnow()}, synchronize_session=False
        )
        db.session.flush()
        return deleted_count

    def get_by_title(title, post_id=None):
        """
        Get a post by title, optionally excluding a specific post_id
        """
        query = Post.query.filter(Post.title == title)
        if post_id:
            query = Post.query.filter(Post.id != post_id)
        return query.first()

    def get_post_by_ids(post_ids):

        return Post.query.filter(Post.id.in_(post_ids)).all()
