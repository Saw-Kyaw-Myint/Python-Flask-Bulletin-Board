import re

from pydantic import BaseModel, field_validator
from typing import Optional


class RestPasswordRequest(BaseModel):
    password: str
    confirm_password: str
    token: Optional[str] = None

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
            "token.missing": "The token is required.",
            "password.missing": "The Password field is required.",
            "password.string_too_short": "The Password must be at least 6 characters.",
            "password.string_too_long": "The Password may not be greater than 20 characters.",
            "password.value_error": "The Password must be 8-20 chars and can include letters, digits, and special chars.",
            "confirm_password.missing": "The Password Confirm field is required.",
            "confirm_password.value_error": "The Password Confirmation and password must match.",
        }
