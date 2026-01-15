from app.extension import ma
from app.models.user import User


class UserListSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = False
        ordered = True
        exclude = ("password", "deleted_at")
