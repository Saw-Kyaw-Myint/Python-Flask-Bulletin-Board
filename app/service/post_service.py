from flask_jwt_extended import get_jwt_identity

from app.dao.post_dao import PostDao
from app.models.post import Post
from app.service.base_service import BaseService
from app.shared.commons import field_error


class PostService(BaseService):

    def filter_paginate(filters, page: int, per_page: int):
        """
        Filter posts and return paginated results.
        """
        posts = PostDao.paginate(filters, page, per_page)

        return posts

    def create_post(payload):
        user_id = get_jwt_identity()
        post = PostDao.get_by_title(payload.title)
        if post:
            field_error("title", "The Title is  already exists.", 402)

        post = Post(
            title=payload.title,
            description=payload.description,
            status=1,
            create_user_id=user_id,
            updated_user_id=user_id,
        )

        return PostDao.create(post)

    def get_post(post_id: int):
        """
        Get post by post id
        """
        post = PostDao.get_post(post_id)
        if not post:
            return ValueError("User don't not exist.")
        return post

    def update_post(payload, id):
        """
        Update Post data
        """
        user_id = get_jwt_identity()
        post = PostDao.get_post(id)
        if not post:
            field_error("post", "Post not found.", 404)
        existing_post = PostDao.get_by_title(payload.title, id)
        if existing_post:
            field_error("title", "The Title is  already exists.", 402)
        post.title = payload.title
        post.description = payload.description
        post.status = payload.status
        post.updated_user_id = user_id

        return post

    def delete_posts(post_ids):
        """
        Delete posts by IDs.
        """
        posts = PostDao.delete_posts(post_ids)
        if not posts:
            raise ValueError("not user found")
        return posts
