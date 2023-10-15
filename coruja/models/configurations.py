from datetime import datetime

from sqlalchemy import event

from ..extensions.database import db
from ..extensions.sessions import session


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
        onupdate=datetime.now,
    )

    def on_update(self):
        change = Change(
            object_old=self.__dict__["_original_state"]
            if "_original_state" in self.__dict__
            else None,
            object_new=self.__dict__,
            user_id=session.user_id,  # type: ignore
        )

        db.session.add(change)
        db.session.commit()


@event.listens_for(BaseTable, "before_update")
def before_update(mapper, connection, target):
    target.on_update()


class Change(BaseTable):
    object_old = db.Column(db.JSON)
    object_new = db.Column(db.JSON)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    user = db.relationship("User", backref="changes", lazy=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object_old = kwargs.get("object_old")
        self.object_new = kwargs.get("object_new")
        self.user_id = kwargs.get("user_id")


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
