from app.extension import ma
from app.models.post import Post


class PostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Post
        ordered = True
        exclude = ("updated_at", "deleted_at")
