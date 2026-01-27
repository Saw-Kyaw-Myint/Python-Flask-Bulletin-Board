import os
from datetime import datetime

from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename

from app.extension import db
from app.request.user_request import UserCreateRequest, UserUpdateRequest
from app.schema.auth_schema import AuthSchema
from app.schema.user_list_schema import UserListSchema
from app.schema.user_schema import UserSchema
from app.service.user_service import UserService
from app.shared.commons import field_error, paginate_response, validate_request
from app.utils.log import log_handler
from config.logging import logger

user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_list = UserListSchema(many=True)
auth_schema = AuthSchema()

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
UPLOAD_DIR = "public/images/profile"


def get_users():
    """
    Return a paginated list of users with optional filters.
    """
    try:
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

        return paginate_response(pagination, user_list)
    except Exception as e:
        log_handler("error", "User Controller : get_users", e)
        return jsonify({"msg": str(e)}), 500


@validate_request(UserCreateRequest)
def create_user(payload):
    """
    Create User
    """
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
        return jsonify({"msg": "Register success"}), 200
    except HTTPException as e:
        db.session.rollback()
        return e
    except Exception as e:
        db.session.rollback()
        log_handler("error", "User Controller : create_user =>", e)
        return jsonify({"msg": str(e)}), 500


def show_user(user_id):
    """
    Get User by user id
    """
    user = UserService.get_user(user_id)
    return jsonify(user_schema.dump(user)), 200


# Update user
@validate_request(UserUpdateRequest)
def update_user(payload, id):
    """
    Update User Information
    """
    file = request.files.get("profile")
    payload_dict = payload.model_dump()
    if file:
        user_id = get_jwt_identity()
        opt_file = optimize_file(file, user_id)
        file_path = opt_file["storage_path"]
        payload_dict["profile"] = opt_file["file_url"]

    try:
        user = UserService.update(payload_dict, id)
        if file:
            file.save(file_path)
        db.session.commit()
        user = auth_schema.dump(user)

        return jsonify({"msg": "user update is success", "user": user}), 200
    except HTTPException as e:
        db.session.rollback()
        return e
    except Exception as e:
        log_handler("error", "User Controller", e)
        db.session.rollback()

        return jsonify({"msg": str(e)}), 500


def delete_users():
    """
    Delete users
    """
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"msg": "empty data"}), 400
    try:
        deleted_user_count = UserService.delete_users(payload)
        db.session.commit()
        return jsonify({"msg": f"{deleted_user_count} users deleted successfully"}), 200
    except ValueError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        log_handler("error", "User Controller : delete_users =>", e)
        db.session.rollback()
        return jsonify({"msg": str(e)}), 500


def lock_users():
    """_Lock users_

    Returns:
        _json_: _Error or Success_
    """
    data = request.get_json(silent=True) or {}
    user_ids = data.get("user_ids")
    if not isinstance(user_ids, list) or not user_ids:
        return jsonify({"msg": "Provide a list of user IDs"}), 400
    try:
        users = UserService.lock_users(user_ids)
        db.session.commit()
        return jsonify({"msg": f"{len(users)} users locked successfully"}), 200
    except ValueError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        log_handler("error", "User Controller : lock_users =>", e)
        db.session.rollback()
        return jsonify({"msg": str(e)}), 500


def unlock_users():
    """
    Unlock users
    """
    data = request.get_json(silent=True) or {}
    user_ids = data.get("user_ids")
    if not isinstance(user_ids, list) or not user_ids:
        return jsonify({"msg": "Provide a list of user IDs"}), 400
    try:
        users = UserService.unlock_users(user_ids)
        db.session.commit()
        return jsonify({"msg": f"{len(users)} users unlocked successfully"}), 200
    except ValueError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        log_handler("error", "User Controller : unlock_users =>", e)
        db.session.rollback()
        return jsonify({"msg": str(e)}), 500


def optimize_file(file, user_id: str, sub_dir: str = "profile"):
    """
    Optimize file
    """
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
