from flask import Blueprint, jsonify, request

from app.controllers.auth_controller import login_user, logout, refresh
from app.controllers.post_controller import (
    create_post,
    delete_posts,
    post_list,
    show_post,
    update_post,
)
from app.controllers.user_controller import (
    create_user,
    delete_users,
    get_users,
    lock_users,
    show_user,
    unlock_users,
    update_user,
)
from app.extension import limiter
from app.middleware.post_middleware import post_middleware
from app.middleware.user_middleware import user_middleware
from app.shared.commons import before_middleware
from config.logging import logger

# ///////// implement Blueprint //////////////////////
user_bp = Blueprint("user", __name__, url_prefix="/api/users")
auth_bp = Blueprint("auth", __name__, url_prefix="/api")
post_bp = Blueprint("post", __name__, url_prefix="/api/posts")


# Apply rate limit to the whole blueprint
# limiter.limit("5 per minute")(user_bp)


# Auth Route
auth_bp.post("/login")(login_user)
auth_bp.post("/refresh")(refresh)
auth_bp.post("/logout")(logout)


# User Route
before_middleware(user_bp, user_middleware)
user_bp.get("/")(get_users)
user_bp.post("/create")(create_user)
user_bp.get("/show/<int:user_id>")(show_user)
user_bp.post("/update/<int:id>")(update_user)
user_bp.post("/multiple-delete")(delete_users)
user_bp.post("/lock")(lock_users)
user_bp.post("/unlock")(unlock_users)


# Post Route
before_middleware(post_bp, post_middleware)
post_bp.get("/")(post_list)
post_bp.get("/show/<int:post_id>")(show_post)
post_bp.post("/create")(create_post)
post_bp.put("/update/<int:id>")(update_post)
post_bp.post("/multiple-delete")(delete_posts)


# export all Blueprint
__all__ = ["user_bp", "auth_bp", "post_bp"]
