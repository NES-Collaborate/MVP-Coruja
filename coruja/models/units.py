from typing import Optional

from ..extensions.database import db
from .configurations import BaseTable
from .users import User

units_administrators = db.Table(
    "units_administrators",
    db.Column("unit_id", db.Integer, db.ForeignKey("unit.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
)

units_staff = db.Table(
    "units_staff",
    db.Column("unit_id", db.Integer, db.ForeignKey("unit.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
)


class Unit(BaseTable):
    description = db.Column(db.String)
    administrators = db.relationship(
        "User",
        secondary=units_administrators,
        backref=db.backref("units_administered", lazy="dynamic"),
    )
    staff = db.relationship(
        "User",
        secondary=units_staff,
        backref=db.backref("units_staffed", lazy="dynamic"),
    )

    is_template = db.Column(db.Boolean, default=False)

    def __init__(
        self,
        *,
        description: Optional[str] = None,
        is_template: Optional[bool] = False
    ) -> None:
        self.description = description
        self.is_template = is_template

    def add_administrator(self, user: User):
        if not self.administrators:
            self.administrators = []

        self.administrators.append(user)

        db.session.commit()
