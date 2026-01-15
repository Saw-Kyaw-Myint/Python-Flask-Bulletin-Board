from marshmallow import fields

from app.extension import ma
from app.models import User


class UserSchema(ma.SQLAlchemyAutoSchema):
    """
    Marshmallow schema for serializing and deserializing User objects.

    This schema maps the User model fields to custom JSON keys and ensures
    that API responses follow a consistent format.
    """

    class Meta:
        model = User
        load_instance = False
        include_fk = True
        # Only include these fields
        fields = (
            "id",
            "name",
            "email",
            "phone",
            "profile_path",
            "role",
            "dob",
            "address",
            "last_login_at",
        )
        ordered = True
