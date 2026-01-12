from app.extension import db


class PasswordReset(db.Model):
    """
    _Password Reset_
    """

    __tablename__ = "password_resets"

    id = db.Column(db.BigInteger, primary_key=True, nullable=False, autoincrement=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    token = db.Column(db.String(255), nullable=False)


# timestamp add sof delete
db.timeStamp(PasswordReset)
db.softDelete(PasswordReset)
