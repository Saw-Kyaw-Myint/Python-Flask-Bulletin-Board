from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., max_length=50)
    password: str
    remember: Optional[bool] = False

    @field_validator("password")
    @classmethod
    def strong_password(cls, v: str) -> str:
        """Validate password strength."""
        if not v:
            return v
        if len(v) < 6 or len(v) > 20:
            raise ValueError()
        if not any(c.isupper() for c in v):
            raise ValueError()
        if not any(c.islower() for c in v):
            raise ValueError()
        if not any(c.isdigit() for c in v):
            raise ValueError()
        if not any(c in "@$!%*?&" for c in v):
            raise ValueError()
        return v

    @classmethod
    def messages(cls):
        return {
            "email.missing": "The Email Address field is required.",
            "email.value_error": "The Email Address field format is invalid.",
            "email.too_long": "The Email may not be greater than 50 characters.",
            "password.missing": "The Password field is required.",
            "password.value_error": "The Password must be 8-20 chars and can include letters, digits, and special chars.",
        }
