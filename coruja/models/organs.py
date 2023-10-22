from typing import Optional

from ..extensions.database import db
from .configurations import BaseTable
from .institution import Institution
from .relationships import organ_administrators, organ_institutions
from .users import User


class Organ(BaseTable):
    name = db.Column(db.String(255), nullable=False)
    cnpj = db.Column(db.String(255), nullable=False, unique=True)
    address = db.Column(db.String(255))
    email = db.Column(db.String(255), nullable=False, unique=True)
    telephone = db.Column(db.String(255))
    is_template = db.Column(db.Boolean, default=False)

    administrators = db.relationship(
        "User",
        secondary=organ_administrators,
        backref=db.backref("organs_administered", lazy=True),
    )

    institutions = db.relationship(
        "Institution",
        secondary=organ_institutions,
        backref=db.backref("organs", lazy=True),
    )

    def __init__(
        self,
        *,
        name: str,
        cnpj: str,
        address: Optional[str] = None,
        email: str,
        telephone: Optional[str] = None,
        is_template: Optional[bool] = False,
    ):
        self.name = name
        self.cnpj = cnpj
        self.address = address
        self.email = email
        self.telephone = telephone
        self.is_template = is_template

    def add_administrator(self, user: User):
        if user not in self.administrators:  # type: ignore
            self.administrators.append(user)
            db.session.commit()

    def add_institution(self, institution: Institution):
        if not self.institutions:
            self.institutions = []

        self.institutions.append(institution)
        db.session.commit()
