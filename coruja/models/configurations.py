from datetime import datetime

from ..extensions.database import db


class BaseTable(db.Model):
    __abstract__ = True

    id = db.Column(
        db.Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now,
        # onupdate=datetime.now,
    )

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}  # type: ignore


class Change(BaseTable):
    object_old = db.Column(db.JSON)
    object_new = db.Column(db.JSON)
    object_type = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    user = db.relationship("User", backref="changes", lazy=True)

    def __init__(self, *, object_old, object_new, user_id, object_type):
        self.object_old = self.serialize_dict(object_old)
        self.object_new = self.serialize_dict(object_new)
        self.user_id = user_id
        self.object_type = object_type

    @staticmethod
    def serialize_dict(d):
        new_dict = {}
        for k, v in d.items():
            if isinstance(v, datetime):
                new_dict[k] = v.isoformat()
            else:
                new_dict[k] = v
        return new_dict


class AccessLog(BaseTable):
    ip = db.Column(db.String(255))
    user_agent = db.Column(db.String(255))
    access_at = db.Column(db.DateTime)
    endpoint = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    user = db.relationship("User", backref="access_logs", lazy=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ip = kwargs.get("ip")
        self.user_agent = kwargs.get("user_agent")
        self.access_at = kwargs.get("access_at")
        self.endpoint = kwargs.get("endpoint")
        self.user_id = kwargs.get("user_id")
