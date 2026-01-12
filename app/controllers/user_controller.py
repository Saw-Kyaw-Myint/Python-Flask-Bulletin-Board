from flask import jsonify, request

from app.request.user_request import UserCreateRequest, UserUpdateRequest
from app.schema.user_schema import UserSchema
from app.service.user_service import UserService
from app.shared.commons import validate_request

user_schema = UserSchema()
users_schema = UserSchema(many=True)


def get_users():
    users = UserService.list()
    return jsonify(users_schema.dump(users)), 200


@validate_request(UserCreateRequest)
def create_user(payload):
    try:
        user = UserService.create(payload)
    except ValueError as e:
        return jsonify({"msg": str(e)}), 409

    return jsonify(user_schema.dump(user)), 201


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
