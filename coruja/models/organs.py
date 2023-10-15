from typing import Optional

from ..extensions.database import db
from .configurations import BaseTable
from .institution import Institution
from .users import User

organ_administrators = db.Table(
    "organ_administrators",
    db.Column(
        "organ_id",
        db.Integer,
        db.ForeignKey("organ.id"),
        primary_key=True,
    ),
    db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey("user.id"),
        primary_key=True,
    ),
)

organ_intitutions = db.Table(
    "organ_intitutions",
    db.Column(
        "organ_id",
        db.Integer,
        db.ForeignKey("organ.id"),
        primary_key=True,
    ),
    db.Column(
        "institution_id",
        db.Integer,
        db.ForeignKey("institution.id"),
        primary_key=True,
    ),
)


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

    intitutions = db.relationship(
        "Institution",
        secondary=organ_intitutions,
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
        if not self.administrators:
            self.administrators = []

        self.administrators.append(user)

        db.session.commit()

    def add_institution(self, institution: Institution):
        if not self.intitutions:
            self.intitutions = []

        self.intitutions.append(institution)

        db.session.commit()
