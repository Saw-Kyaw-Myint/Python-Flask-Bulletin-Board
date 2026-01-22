from app.dao.post_dao import PostDao
from app.service.base_service import BaseService


class PostService(BaseService):

    def filter_paginate(filters, page: int, per_page: int):
        posts = PostDao.paginate(filters, page, per_page)

        return posts
