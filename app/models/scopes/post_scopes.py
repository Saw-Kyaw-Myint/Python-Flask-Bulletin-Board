from datetime import datetime

from sqlalchemy import func, or_

from app.models.post import Post
from app.utils.decorators import static_all_methods
from config.logging import logger


@static_all_methods
class PostScopes:
    """
    Reusable query scopes for the Post model.
    """

    def active(query):
        """Filter out deleted posts."""
        return query.filter(Post.deleted_at.is_(None))

    def filter_title_description(query, filters):
        """Filter posts by title and/or description."""
        title = (filters.get("name") or "").strip()
        description = (filters.get("description") or "").strip()

        if title or description:
            conditions = []

            if title:
                conditions.append(Post.title.ilike(f"%{title}%"))

            if description:
                conditions.append(Post.description.ilike(f"%{description}%"))

            query = query.filter(or_(*conditions))

        return query

    def filter_status(query, filters):
        """Filter posts by status."""
        status = filters.get("status")
        if status is not None:
            query = query.filter(Post.status == status)
        return query

    def filter_date(query, filters):
        """Filter posts by created date (YYYY-MM-DD)."""
        date_str = filters.get("date")

        try:
            if date_str:
                created_date = datetime.fromisoformat(date_str)
                query = query.filter(func.date(Post.created_at) == created_date.date())
        except ValueError as e:
            logger.error(f"Invalid date format: {e}")

        return query

    def latest(query):
        """Order posts by latest."""
        return query.order_by(Post.id.desc())
