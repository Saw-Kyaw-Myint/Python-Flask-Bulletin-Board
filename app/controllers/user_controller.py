from flask import jsonify, request

from app.request.user_request import UserCreateRequest, UserUpdateRequest
from app.schema.user_schema import UserSchema
from app.service.user_service import UserService
from app.shared.commons import validate_request
import os
from werkzeug.utils import secure_filename
from config.logging import logger

user_schema = UserSchema()
users_schema = UserSchema(many=True)


def get_users():
    users = UserService.list()
    return jsonify(users_schema.dump(users)), 200


@validate_request(UserCreateRequest)
def create_user(payload):
    UPLOAD_DIR = "public/images/profile"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    # profile file
    file =request.files.get('profile')
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

    return jsonify({
        "msg": "Register success",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }), 201


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


# Delete user
def delete_user(user_id):
    success = UserService.delete(user_id)
    if not success:
        return jsonify({"msg": "User not found"}), 404
    return jsonify({"msg": "User deleted"}), 200
