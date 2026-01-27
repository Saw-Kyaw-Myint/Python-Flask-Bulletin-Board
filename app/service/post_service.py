from flask import jsonify
from flask_jwt_extended import get_jwt_identity

from app.dao.post_dao import PostDao
from app.extension import db
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
            field_error("title", "The Title is  already exists.", 400)

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
            field_error("title", "The Title is  already exists.", 400)
        post.title = payload.title
        post.description = payload.description
        post.status = payload.status
        post.updated_user_id = user_id

        return post

    def delete_posts(payload):
        """
        Delete posts by IDs.
        """
        select_all = payload.get("all", False)
        post_ids = payload.get("post_ids", [])
        exclude_ids = payload.get("exclude_ids", [])
        if select_all:
            posts = PostDao.delete_all_posts(exclude_ids)
        else:
            if not isinstance(post_ids, list) or not post_ids:
                raise ValueError("Provide post id list.")
            posts = PostDao.delete_posts(post_ids)
        return posts

    def get_post_by_ids(post_ids):
        """
        Get posts by using post_ids
        """
        return PostDao.get_post_by_ids(post_ids)
