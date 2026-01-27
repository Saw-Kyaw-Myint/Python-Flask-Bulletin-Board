from datetime import datetime
from itertools import batched

from sqlalchemy.orm import joinedload

from app.dao.base_dao import BaseDao
from app.extension import db
from app.models.post import Post
from app.models.scopes.post_scopes import PostScopes
from app.shared.commons import BATCH_SIZE
from config.logging import logger


class PostDao(BaseDao):

    def paginate(filters, page: int, per_page: int):
        """
        Return filtered and paginated posts.
        """
        query = Post.query

        query = PostScopes.active(query)
        query = PostScopes.filter_title_description(query, filters)
        query = PostScopes.filter_status(query, filters)
        query = PostScopes.filter_date(query, filters)
        query = PostScopes.latest(query)

        return query.paginate(page=page, per_page=per_page, error_out=False)

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
        """
        Get posts by using post_ids
        """
        return Post.query.filter(Post.id.in_(post_ids)).all()
