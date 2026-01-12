from flask import Blueprint

from app.controllers.auth_controller import get_me, login_user
from app.controllers.user_controller import (
    create_user,
    delete_user,
    get_users,
    update_user,
)
from app.extension import limiter
from app.middleware.user_middleware import user_middleware
from app.shared.commons import before_middleware

# ///////// implement Blueprint //////////////////////
user_bp = Blueprint("user", __name__, url_prefix="/users")
auth_bp = Blueprint("auth", __name__)


# Apply rate limit to the whole blueprint
# limiter.limit("5 per minute")(user_bp)


# Auth Route
auth_bp.post("/login")(login_user)
auth_bp.get("/me")(get_me)

# User Route
before_middleware(user_bp, user_middleware)
user_bp.get("/")(get_users)
user_bp.post("/create")(create_user)
user_bp.put("/update/<int:user_id>")(update_user)
user_bp.delete("/delete/<int:user_id>")(delete_user)

# export all Blueprint
__all__ = ["user_bp", "auth_bp"]
