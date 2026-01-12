from app.extension import db


class Post(db.Model):
    """
    _Post Table_
    """

    __tablename__ = "posts"

    id = db.Column(db.BigInteger, primary_key=True, nullable=False, autoincrement=True)
    title = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    create_user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    updated_user_id = db.Column(
        db.BigInteger, db.ForeignKey("users.id"), nullable=False
    )
    deleted_user_id = db.Column(db.BigInteger)

    creator = db.relationship(
        "User", foreign_keys=[create_user_id], backref="posts_created"
    )
    updater = db.relationship(
        "User", foreign_keys=[updated_user_id], backref="posts_updated"
    )

    _long_names = {
        id: "ID",
        title: "Post Title",
        description: "Post Description",
        status: "Post Status",
        create_user_id: "Created User ID",
        updated_user_id: "Updated User ID",
        deleted_user_id: "Deleted User ID",
    }

    def long_name(self, col):
        return self._long_names.get(col, None)


# timestamp add sof delete
db.timeStamp(Post)
db.softDelete(Post)
