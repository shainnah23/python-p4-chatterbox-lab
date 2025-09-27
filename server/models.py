from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
try:
    from sqlalchemy_serializer import SerializerMixin
except Exception:
    # Minimal fallback if sqlalchemy-serializer isn't installed in the test env.
    class SerializerMixin:
        def to_dict(self):
            # naive conversion: pull columns from __table__ if present
            if hasattr(self, '__table__'):
                return {c.name: getattr(self, c.name) for c in self.__table__.columns}
            return {}

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Message(db.Model, SerializerMixin):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String)
    username = db.Column(db.String)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
