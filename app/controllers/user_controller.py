import os
from datetime import datetime

from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from werkzeug.utils import secure_filename

from app.extension import db
from app.request.user_request import UserCreateRequest, UserUpdateRequest
from app.schema.auth_schema import AuthSchema
from app.schema.user_list_schema import UserListSchema
from app.schema.user_schema import UserSchema
from app.service.user_service import UserService
from app.shared.commons import field_error, validate_request
from config.logging import logger

user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_list = UserListSchema(many=True)
auth_schema = AuthSchema()

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
UPLOAD_DIR = "public/images/profile"


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
    file = request.files.get("profile")
    payload_dict = payload.model_dump()
    if not file:
        field_error("profile", "The Profile field is required", 422)
    user_id = payload_dict["user_id"]
    opt_file = optimize_file(file, user_id)
    payload_dict["profile"] = opt_file["file_url"]

    try:
        UserService.create(payload_dict)
        file.save(opt_file["storage_path"])
        db.session.commit()

        return (
            jsonify({"message": "Register success"}),
            201,
        )
    except Exception as e:
        logger.error("User Controller : create_user")
        logger.error(e)
        db.session.rollback()

        return jsonify({"message": str(e)}), 409


def show_user(user_id):
    user = UserService.get_user(user_id)
    return jsonify(user_schema.dump(user)), 200


# Update user
@validate_request(UserUpdateRequest)
def update_user(payload, id):
    file = request.files.get("profile")
    payload_dict = payload.model_dump()
    if file:
        user_id = payload_dict["user_id"]
        opt_file = optimize_file(file, user_id)
        file_path = opt_file["storage_path"]
        payload_dict["profile"] = opt_file["file_url"]

    try:
        user = UserService.update(payload_dict, id)
        if file:
            file.save(file_path)
        db.session.commit()
        user = auth_schema.dump(user)

        return (
            jsonify({"message": "user update is success", "user": user}),
            201,
        )
    except Exception as e:
        logger.error("User Controller : update_user")
        logger.error(e)
        db.session.rollback()
        return jsonify({"message": str(e)}), 409


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


def optimize_file(file, user_id: str, sub_dir: str = "profile"):
    user_dir = os.path.join(UPLOAD_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    ext = os.path.splitext(file.filename)[1].lower().lstrip(".")

    if ext not in ALLOWED_EXTENSIONS:
        field_error("profile", "The profile must be a file  of type.jpg,png", 422)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    original_filename = secure_filename(file.filename)
    name, ext = os.path.splitext(original_filename)
    new_filename = f"{name}_{timestamp}{ext}"
    file_path = os.path.join(user_dir, new_filename)

    return {
        "storage_path": file_path,
        "file_url": f"{sub_dir}/{user_id}/{new_filename}",
    }
