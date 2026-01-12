# app/models/base_model.py
from datetime import datetime

from app.extension import db


class BaseModel(db.Model):
    __abstract__ = True
