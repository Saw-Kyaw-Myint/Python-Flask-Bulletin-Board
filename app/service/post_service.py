from flask import jsonify
from flask_jwt_extended import get_jwt_identity

from app.dao.post_dao import PostDao
from app.extension import db
from app.models.post import Post
from app.service.base_service import BaseService
from app.shared.commons import field_error, response_valid_request
from app.utils.csv import CSV
from app.utils.request import clean_filters, request_query
from config.logging import logger


class PostService(BaseService):

    def filter_paginate(filters, page: int, per_page: int):
        """Filter posts and return paginated results."""
        posts = PostDao.paginate(filters, page, per_page)
        return posts

    def create_post(payload):
        """Create post."""
        user_id = get_jwt_identity()
        invalid_response = PostService.check_create_update_invalid_request(payload)
        if invalid_response:
            return invalid_response
        post = Post(
            title=payload.title,
            description=payload.description,
            status=1,
            create_user_id=user_id,
            updated_user_id=user_id,
        )
        post = PostDao.create(post)

        return {"post": post}

    def get_post(post_id: int):
        """Get post by post id"""
        post = PostDao.get_post(post_id)
        if not post:
            return ValueError("Post don't not exist.")

        return post

    def update_post(payload, id):
        """Update Post data"""
        user_id = get_jwt_identity()
        invalid_response = PostService.check_create_update_invalid_request(payload, id)
        if invalid_response:
            return invalid_response
        post = PostDao.find_one(id=id)
        post.title = payload.title
        post.description = payload.description
        post.status = payload.status
        post.updated_user_id = user_id

        return {"post": post}

    def delete_posts(payload):
        """Delete posts by IDs."""
        select_all = payload.get("all", False)
        post_ids = payload.get("post_ids", [])
        exclude_ids = payload.get("exclude_ids", [])
        if select_all:
            filters = payload.get("filters", {})
            posts = PostDao.delete_all_posts(exclude_ids, filters)
        else:
            if not isinstance(post_ids, list) or not post_ids:
                raise ValueError("Provide post id list.")
            posts = PostDao.delete_posts(post_ids)

        return posts

    def get_post_by_ids(post_ids):
        """Get posts by using post_ids"""
        return PostDao.get_post_by_ids(post_ids)

    def export_posts_csv(payload):
        """Stream Export CSV"""
        select_all = payload.get("all", False)
        post_ids = payload.get("post_ids", [])
        exclude_ids = payload.get("exclude_ids", [])
        if select_all:
            filters = payload.get("filters", {})
            posts = PostDao.stream_all_posts(exclude_ids, filters)
        else:
            posts = PostDao.stream_posts_by_ids(post_ids)
        stream_posts = CSV.post_csv_generator(posts)

        return stream_posts

    def check_create_update_invalid_request(payload, id=None):
        post = PostDao.get_by_title(payload.title, id)
        if post:
            field_error("title", "The Title is  already taken.", 400)
        if not payload.is_valid_request:
            return response_valid_request()
