import csv
from io import StringIO

from flask import Response, jsonify, request
from werkzeug.exceptions import HTTPException

from app.extension import db
from app.request.post_request import CreatePostRequest, UpdatePostRequest
from app.schema.post_schema import PostSchema
from app.service.post_service import PostService
from app.shared.commons import paginate_response, raise_error, validate_request
from app.utils.log import log_handler
from config.logging import logger

posts_schema = PostSchema(many=True)
post_schema = PostSchema()


def post_list():
    """
    Return a paginated list of posts with optional filters.
    """
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


@validate_request(CreatePostRequest)
def create_post(payload):
    """
    Create post
    """
    try:
        PostService.create_post(payload)
        db.session.commit()
        return jsonify({"msg": "Post creation is success."}), 200
    except HTTPException as e:
        db.session.rollback()
        raise e
    except Exception as e:
        db.session.rollback()
        log_handler("error", "Post Controller : create_post =>", e)
        return jsonify({"msg": str(e)}), 500


def show_post(post_id):
    """
    Get User by user id
    """
    post = PostService.get_post(post_id)
    return jsonify(post_schema.dump(post)), 200


@validate_request(UpdatePostRequest)
def update_post(payload, id):
    """
    Update post
    """
    try:
        post = PostService.update_post(payload, id)
        db.session.commit()
        return jsonify({"msg": f"{(post.id)} Post update successfully"}), 200
    except HTTPException as e:
        db.session.rollback()
        return e
    except Exception as e:
        db.session.rollback()
        log_handler("error", "Post Controller: update_post", e)
        return jsonify({"msg": str(e)}), 500


def delete_posts():
    """
    Delete posts
    """
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"msg": "empty data"}), 400
    try:
        posts = PostService.delete_posts(payload)
        db.session.commit()
        return jsonify({"msg": f"{posts} posts deleted successfully"}), 200
    except ValueError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        db.session.rollback()
        log_handler("error", "Post Controller : delete_posts", e)
        return jsonify({"msg": str(e)}), 500


def export_csv():
    """
    Export CSV
    """
    try:
        data = request.get_json(silent=True) or {}
        post_ids = data.get("post_ids", [])

        posts = PostService.get_post_by_ids(post_ids)

        if not posts:
            raise_error("msg", "Post not found.", 404)

        output = StringIO()

        fieldnames = [
            "id",
            "title",
            "description",
            "status",
            "created_user_id",
            "updated_user_id",
            "deleted_user_id",
            "deleted_at",
            "created_at",
            "updated_at",
        ]

        writer = csv.writer(output, quoting=csv.QUOTE_ALL)

        writer.writerow(fieldnames)

        for post in posts:
            writer.writerow(
                [
                    post.id,
                    post.title,
                    post.description,
                    post.status,
                    post.created_user_id,
                    post.updated_user_id,
                    post.deleted_user_id,
                    post.deleted_at,
                    post.created_at,
                    post.updated_at,
                ]
            )

        response = Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=posts.csv"},
        )

        return response
    except Exception as e:
        log_handler("error", "Post Controller : export_csv =>", e)
        return jsonify({"message": str(e)}), 500
