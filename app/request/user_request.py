# app/request/user_request.py
from pydantic import BaseModel, EmailStr, Field


class UserCreateRequest(BaseModel):
    """
    Schema for validating user creation requests.

    This Pydantic model is used to validate incoming JSON payloads
    when creating a new user via the API.

    Attributes:
        name (str): Name of the user. Must be between 3 and 50 characters.
        email (EmailStr): Valid email address for the user.

    Example JSON payload:
        {
            "name": "John Doe",
            "email": "john@example.com"
        }
    """

    name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserUpdateRequest(BaseModel):
    name: str = Field(None, min_length=3, max_length=50)
    email: EmailStr
