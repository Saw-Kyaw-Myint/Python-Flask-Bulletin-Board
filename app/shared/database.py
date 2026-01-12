# app/extension/db_extensions.py
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, DateTime


def timeStamp(model_class):
    """Attach created_at and updated_at columns to a model."""
    model_class.created_at = Column(DateTime, default=datetime.utcnow)
    model_class.updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


def softDelete(model_class):
    """Attach deleted_at column and soft delete / restore methods."""
    model_class.deleted_at = Column(DateTime, nullable=True)

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()

    def restore(self):
        self.deleted_at = None

    model_class.soft_delete = soft_delete
    model_class.restore = restore
