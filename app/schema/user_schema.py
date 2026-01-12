from marshmallow import fields

from app.extension import ma
from app.models import User


class UserSchema(ma.SQLAlchemyAutoSchema):
    """
    Marshmallow schema for serializing and deserializing User objects.

    This schema maps the User model fields to custom JSON keys and ensures
    that API responses follow a consistent format.

    Field Mappings:
        - userId (int): Maps to User.id
        - fullName (str): Maps to User.name
        - emailAddress (str): Maps to User.email

    Meta Options:
        - model: Specifies the SQLAlchemy model (User) to bind the schema to.
        - load_instance: Allows deserialization into SQLAlchemy model instances.
        - include_fk: Includes foreign key fields in the schema if present.
        - fields: Restricts the output to only the specified fields.

    Example Serialized Output:
        {
            "userId": 1,
            "fullName": "John Doe",
            "emailAddress": "john@example.com"
        }
    """

    # Example: rename fields or change format
    userId = fields.Int(attribute="id")
    fullName = fields.Str(attribute="name")
    emailAddress = fields.Email(attribute="email")

    class Meta:
        model = User
        load_instance = True
        include_fk = True
        # Only include these fields
        fields = ("userId", "fullName", "emailAddress")
