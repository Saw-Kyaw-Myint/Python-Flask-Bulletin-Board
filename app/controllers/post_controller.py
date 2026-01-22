from flask import jsonify, request

from app.schema.post_schema import PostSchema
from app.service.post_service import PostService
from app.shared.commons import paginate_response

posts_schema = PostSchema(many=True)


def post_list():
    filters = {
        "name": request.args.get("name", type=str),
        "description": request.args.get("description", type=str),
        "status": request.args.get("status", type=int),
        "date": request.args.get("date"),
    }
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    posts = PostService.filter_paginate(filters, page, per_page)

    return paginate_response(posts, posts_schema)
