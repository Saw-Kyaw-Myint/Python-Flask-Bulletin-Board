from marshmallow import fields

from app.extension import ma
from app.models import User


class UserRelationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = ("id", "name", "email")


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
            "creator",
            "created_at",
            "create_user_id",
            "updater",
            "updated_at",
            "updated_user_id",
        )
        ordered = True

    creator = fields.Nested(
        UserRelationSchema, only=("id", "name", "email"), dump_only=True
    )

    updater = fields.Nested(
        UserRelationSchema, only=("id", "name", "email"), dump_only=True
    )
