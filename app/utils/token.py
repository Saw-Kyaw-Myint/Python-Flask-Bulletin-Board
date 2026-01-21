import hashlib
from datetime import datetime

from app.extension import db
from app.models.refresh_token import RefreshToken


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def save_refresh_token(user_id, refresh_token, expires_at):
    token = RefreshToken(
        user_id=user_id, token_hash=hash_token(refresh_token), expires_at=expires_at
    )
    db.session.add(token)


def revoke_refresh_token(refresh_token):
    token_hash = hash_token(refresh_token)
    token = RefreshToken.query.filter_by(token_hash=token_hash, revoked=False).first()
    if token:
        token.revoked = True


def revoke_all_refresh_token(user_id):
    RefreshToken.query.filter_by(user_id=user_id).update({"revoked": True})


def is_refresh_token_revoked(refresh_token) -> bool:
    token_hash = hash_token(refresh_token)
    token = RefreshToken.query.filter_by(token_hash=token_hash).first()

    return (not token) or token.revoked or token.expires_at < datetime.utcnow()
