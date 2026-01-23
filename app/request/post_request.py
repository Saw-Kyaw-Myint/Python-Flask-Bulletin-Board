from pydantic import BaseModel, Field, field_validator


class CreatePostRequest(BaseModel):
    title: str = Field(..., max_length=255)
    description: str

    @classmethod
    def messages(cls):
        return {
            "title.missing": "The Title field is required.",
            "title.string_too_long": "The Title field must not be greater than 255.",
            "description.missing": "The Description field is required.",
        }


class UpdatePostRequest(BaseModel):
    title: str = Field(..., max_length=255)
    description: str
    status: int

    @classmethod
    def messages(cls):
        return {
            "title.missing": "The Title field is required.",
            "title.string_too_long": "The Title field must not be greater than 255.",
            "description.missing": "The Description field is required.",
        }
