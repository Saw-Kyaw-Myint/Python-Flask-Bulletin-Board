import os

from flask import jsonify, request
from werkzeug.utils import secure_filename

from app.request.user_request import UserCreateRequest, UserUpdateRequest
from app.schema.user_list_schema import UserListSchema
from app.schema.user_schema import UserSchema
from app.service.user_service import UserService
from app.shared.commons import validate_request
from config.logging import logger

user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_list = UserListSchema(many=True)


def get_users():
    filters = {
        "name": request.args.get("name", type=str),
        "email": request.args.get("email", type=str),
        "role": request.args.get("role", type=int),
        "start_date": request.args.get("start_date"),
        "end_date": request.args.get("end_date"),
    }

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = UserService.filter_paginate(filters, page, per_page)

    return jsonify(
        {
            "data": user_list.dump(pagination.items),
            "meta": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages,
            },
        }
    )


@validate_request(UserCreateRequest)
def create_user(payload):
    UPLOAD_DIR = "public/images/profile"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    # profile file
    file = request.files.get("profile")
    if not file:
        return jsonify({"profile": "The Profile field is required"}), 422
    ext = os.path.splitext(file.filename)[1]
    timestamp = file.filename
    filename = secure_filename(f"image_{timestamp}")

    payload_dict = payload.model_dump()
    payload_dict["profile"] = filename
    try:
        user = UserService.create(payload_dict)
        file.save(os.path.join(UPLOAD_DIR, filename))
    except ValueError as e:
        return jsonify({"msg": str(e)}), 409

    return (
        jsonify(
            {
                "msg": "Register success",
                "user": {"id": user.id, "name": user.name, "email": user.email},
            }
        ),
        201,
    )


# Update user
@validate_request(UserUpdateRequest)
def update_user(payload, user_id):
    try:
        user = UserService.update(user_id, payload)
        if not user:
            return jsonify({"msg": "User not found"}), 404
    except ValueError as e:
        return jsonify({"msg": str(e)}), 409
    return jsonify(user_schema.dump(user)), 200


def delete_users():
    """_Delete users_

    Returns:
        _json_: _Error or Success_
    """
    data = request.get_json() or {}
    user_ids = data.get("user_ids")
    if not isinstance(user_ids, list) or not user_ids:
        return jsonify({"msg": "Provide a list of user IDs"}), 400
    try:
        users = UserService.delete_users(user_ids)
        return jsonify({"msg": f"{len(users)} users deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"msg": str(e)}), 404


def lock_users():
    """_Lock users_

    Returns:
        _json_: _Error or Success_
    """
    data = request.get_json() or {}
    user_ids = data.get("user_ids")
    if not isinstance(user_ids, list) or not user_ids:
        return jsonify({"msg": "Provide a list of user IDs"}), 400
    try:
        users = UserService.lock_users(user_ids)
        return jsonify({"msg": f"{len(users)} users locked successfully"}), 200
    except ValueError as e:
        return jsonify({"msg": str(e)}), 404


def unlock_users():
    """_Unlock users_

    Returns:
        _json_: _Error or Success_
    """
    data = request.get_json() or {}
    user_ids = data.get("user_ids")
    if not isinstance(user_ids, list) or not user_ids:
        return jsonify({"msg": "Provide a list of user IDs"}), 400
    try:
        users = UserService.unlock_users(user_ids)
        return jsonify({"msg": f"{len(users)} users unlocked successfully"}), 200
    except ValueError as e:
        return jsonify({"msg": str(e)}), 404
