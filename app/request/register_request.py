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

class RegisterRequest(BaseModel):
    """
    Schema for validating user creation requests.
    """

    name: str
    email: EmailStr = Field(..., max_length=50)
    password: NonEmptyStr
    confirm_password: NonEmptyStr


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
            "password.value_error": "The Password must be 8-20 chars and can include letters, digits, and special chars.",
            "confirm_password.missing": "The Password Confirm field is required.",
            "confirm_password.value_error": "The Password Confirmation and password must match.",
        }
