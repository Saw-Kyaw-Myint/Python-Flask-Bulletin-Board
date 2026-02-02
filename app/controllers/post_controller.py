import json
import os
import tempfile

import redis
from flask import Response, jsonify, request, stream_with_context
from werkzeug.exceptions import HTTPException

from app.extension import db
from app.request.post_request import CreatePostRequest, UpdatePostRequest
from app.schema.post_schema import PostSchema
from app.service.post_service import PostService
from app.shared.commons import (
    paginate_response,
    raise_error,
    response_valid_request,
    validate_request,
)
from app.task.import_posts import import_posts_from_csv
from app.utils.log import log_handler
from app.utils.request import request_query
from config.celery import CeleryConfig
from config.logging import logger

posts_schema = PostSchema(many=True)
post_schema = PostSchema()
r = redis.Redis.from_url(f"{CeleryConfig.REDIS_URL}/1")


def post_list():
    """Return a paginated list of posts with optional filters."""
    filters = request_query(
        {"name": str, "description": str, "status": int, "date": str}
    )
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    posts = PostService.filter_paginate(filters, page, per_page)
    return paginate_response(posts, posts_schema)


@validate_request(CreatePostRequest)
def create_post(payload):
    """Create post"""
    try:
        post = PostService.create_post(payload)
        if post.get("is_valid_request", False):
            return jsonify({"is_valid_request": True}), 202
        db.session.commit()
        return jsonify({"msg": "Post creation is success."}), 200
    except HTTPException as e:
        db.session.rollback()
        raise e
    except Exception as e:
        db.session.rollback()
        log_handler("error", "Post Controller : create_post =>", e)
        return jsonify({"msg": str(e)}), 500


def ai_review(content: str) -> dict:
    """
    Perform an AI review on the content.
    This is a dummy example. Replace with actual AI API call.
    """
    # Here you could call OpenAI GPT API or any AI model
    review_result = {
        "content": content,
        "review_score": 8,  # example score out of 10
        "comments": ["Good structure", "Consider shortening some paragraphs"]
    }
    return review_result

def show_post(post_id):
    """Get Post by ID and perform AI review"""
    post = PostService.get_post(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    post_data = post_schema.dump(post)
    
    # Run AI review on the post content
    ai_result = ai_review(post_data.get("content", ""))

    return jsonify({
        "post": post_data,
        "ai_review": ai_result
    }), 200

@validate_request(UpdatePostRequest)
def update_post(payload, id):
    """Update post"""
    try:
        post = PostService.update_post(payload, id)
        if post.get("is_valid_request", False):
            return jsonify(response_valid_request()), 202
        db.session.commit()
        return (
            jsonify({"msg": f"{(post.get('post').id)} Post update successfully"}),
            200,
        )
    except HTTPException as e:
        db.session.rollback()
        return e
    except Exception as e:
        db.session.rollback()
        log_handler("error", "Post Controller: update_post", e)
        return jsonify({"msg": str(e)}), 500


def delete_posts():
    """Delete posts"""
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


def stream_csv_export():
    """Export CSV"""
    try:
        payload = request.get_json(silent=True) or {}
        generator = PostService.export_posts_csv(payload)

        return Response(
            stream_with_context(generator),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=posts.csv"},
        )
    except Exception as e:
        log_handler("error", "Post Controller : stream_csv_export =>", e)
        return jsonify({"message": str(e)}), 500


def import_csv():
    """CSV Import"""
    try:
        file = request.files.get("file")
        MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB
        if not file:
            return jsonify({"msg": "CSV file required"}), 400
        filename = file.filename
        ext = os.path.splitext(filename)[1].lower()
        if ext != ".csv":
            return jsonify({"msg": "The CSV File field is required"}), 400
        # Check file size (2MB)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        if file_size > MAX_FILE_SIZE:
            return jsonify({"msg": "The CSV File size must be greater than 2MB."}), 400
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        file.save(tmp.name)
        task = import_posts_from_csv.delay(tmp.name)
        return jsonify({"msg": "Import started", "task_id": task.id}), 200
    except Exception as e:
        log_handler("error", "Post Controller :  import csv =>", e)
        return jsonify({"msg": str(e)}), 500


def csv_progress(task_id):
    """Get CSV upload progress from redis"""
    progress = r.get(f"csv_progress:{task_id}")
    status = r.get(f"csv_status:{task_id}")
    errors = r.get(f"csv_errors:{task_id}")
    response = {
        "progress": int(progress) if progress else 0,
        "status": status.decode() if status else "PENDING",
    }
    if response["status"] == "FAILURE":
        response["errors"] = json.loads(errors.decode()) if errors else []
    return jsonify(response)
