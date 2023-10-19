from typing import Optional

from ..extensions.database import db
from .configurations import BaseTable
from .relationships import unit_analysis, units_administrators, units_staff
from .users import User


class Unit(BaseTable):
    description = db.Column(db.String)
    is_template = db.Column(db.Boolean, default=False)

    analysis = db.relationship(
        "Analysis",
        secondary=unit_analysis,
        backref=db.backref("units", lazy="dynamic"),
    )
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
