from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., max_length=50)
    password: str = Field(
        ...,
        min_length=6,
        max_length=20,
        pattern=r"^[A-Za-z\d!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]{8,20}$",
    )
    remember:Optional[bool] = False

    @classmethod
    def messages(cls):
        return {
            "email.missing": "The Email Address field is required.",
            "email.value_error": "The Email Address field format is invalid.",
            "email.too_long": "The Email may not be greater than 50 characters.",
            "password.missing": "The Password field is required.",
            "password.string_too_short": "The Password must be at least 6 characters.",
            "password.string_too_long": "The Password may not be greater than 20 characters.",
            "password.string_pattern_mismatch": "The Password must be 8-20 chars and can include letters, digits, and special chars.",
        }
