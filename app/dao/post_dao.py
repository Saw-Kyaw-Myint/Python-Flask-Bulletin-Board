from datetime import datetime

from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from app.dao.base_dao import BaseDao
from app.extension import db
from app.models.post import Post
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
        Delete posts by post ids
        """
        posts = Post.query.filter(
            Post.id.in_(post_ids), Post.deleted_at.is_(None)
        ).all()
        for post in posts:
            post.soft_delete()
        db.session.commit()
        return posts

    def get_by_title(title, post_id):
        """
        Get post by title
        """
        return Post.query.filter(Post.title == title, Post.id != post_id).first()
