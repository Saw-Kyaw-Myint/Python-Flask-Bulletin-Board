# app/request/user_request.py
import os
import re
from datetime import date
from typing import Any, Optional

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    constr,
    field_validator,
    model_validator,
)

from app.shared.commons import field_error
from config.logging import logger

NonEmptyStr = constr(min_length=1, strip_whitespace=True)


class UserCreateRequest(BaseModel):
    """
    Schema for validating user creation requests.
    """

    user_id: int
    name: NonEmptyStr
    email: EmailStr = Field(..., max_length=50)
    password: str
    confirm_password: NonEmptyStr
    role: int = Field(..., ge=0, le=1)
    phone: Optional[str] = None
    address: NonEmptyStr
    dob: Optional[date | str] = None
    profile: Any = None

    @field_validator("profile")
    def file_required(cls, v):
        if not v:
            raise ValueError("The Profile field is required")
        return v

    @field_validator("password")
    @classmethod
    def strong_password(cls, v: str) -> str:
        if not v:
            return v
        if not re.fullmatch(r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{6,20}", v):
            raise ValueError(
                "Password must be 6–20 chars and include upper, lower, number, and special character"
            )
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info: Any):
        if "password" in info.data:
            password = info.data["password"]
            if v != password:
                raise ValueError("Passwords do not match")
        return v

    @classmethod
    def messages(cls):
        return {
            "name.missing": "The Name field is required.",
            "email.missing": "The Email field is required.",
            "email.value_error": "The Email Address format is invalid.",
            "email.too_long": "The Email may not be greater than 50 characters.",
            "password.missing": "The Password field is required.",
            "password.string_too_short": "The Password must be at least 6 characters.",
            "password.string_too_long": "The Password may not be greater than 20 characters.",
            "password.value_error": "The Password must be 8-20 chars and can include letters, digits, and special chars.",
            "confirm_password.missing": "The Password Confirm field is required.",
            "confirm_password.value_error": "The Password Confirmation and password must match.",
            "role.missing": "The Role field is required.",
            "address.missing": "The Address field is required.",
            "profile.value_error": "The Profile field is required.",
        }


class UserUpdateRequest(BaseModel):
    """
    Schema for validating user creation requests.
    """

    name: NonEmptyStr
    email: EmailStr = Field(..., max_length=50)
    password: str = None
    confirm_password: str = None
    role: int = Field(..., ge=0, le=1)
    phone: Optional[str] = None
    dob: Optional[date] = None
    profile: Any = None
    address: NonEmptyStr

    @field_validator("profile")
    def file_required(cls, v):
        if not v:
            raise ValueError("The Profile field is required")
        return v

    @field_validator("password")
    @classmethod
    def strong_password(cls, v: str) -> str:
        if not v:
            return v
        if not re.fullmatch(r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{6,20}", v):
            raise ValueError(
                "Password must be 6–20 chars and include upper, lower, number, and special character"
            )
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info: Any):
        if "password" in info.data:
            password = info.data["password"]
            if password is not None and v != password:
                raise ValueError("Passwords do not match")
        return v

    @classmethod
    def messages(cls):
        return {
            "name.missing": "The Name field is required.",
            "email.missing": "The Name field is required.",
            "email.value_error": "The Email Address format is invalid.",
            "email.too_long": "The Email may not be greater than 50 characters.",
            "password.missing": "The Password field is required.",
            "password.string_too_short": "The Password must be at least 6 characters.",
            "password.string_too_long": "The Password may not be greater than 20 characters.",
            "password.value_error": "The Password must be 8-20 chars and can include letters, digits, and special chars.",
            "confirm_password.missing": "The Password Confirm field is required.",
            "confirm_password.value_error": "The Password Confirmation and password must match.",
            "role.missing": "The Role field is required.",
            "address.missing": "The Address field is required.",
            "profile.value_error": "The Profile field is required.",
        }
