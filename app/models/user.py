from datetime import datetime

from app.extension import db


class User(db.Model):
    """
    _User Table_
    """

    __tablename__ = "users"

    id = db.Column(db.BigInteger, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255))
    profile_path = db.Column(db.String(255))
    role = db.Column(db.Boolean, default=True)
    dob = db.Column(db.DateTime)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    lock_flg = db.Column(db.Boolean, default=False)
    lock_count = db.Column(db.Integer, default=False)
    last_lock_at = db.Column(db.DateTime)
    last_login_at = db.Column(db.DateTime)
    create_user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"))
    updated_user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"))
    deleted_user_id = db.Column(db.BigInteger)

    creator = db.relationship(
        "User", foreign_keys=[create_user_id], remote_side="User.id", uselist=False
    )

    updater = db.relationship(
        "User", foreign_keys=[updated_user_id], remote_side="User.id", uselist=False
    )

    _long_names = {
        id: "ID",
        name: "Name",
        email: "Email",
        password: "Password",
        profile_path: "Profile Path",
        role: " Role",
        dob: "Date Of Birth",
        phone: "Phone",
        address: "Address",
    }

    def long_name(self, col):
        return self._long_names.get(col, None)


# timestamp add sof delete
db.timeStamp(User)
db.softDelete(User)
