from typing import Optional

from ..extensions.database import db
from .configurations import BaseTable

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


class Organ(BaseTable):
    name = db.Column(db.String(255), nullable=False)
    cnpj = db.Column(db.String(255), nullable=False, unique=True)
    address = db.Column(db.String(255))
    email = db.Column(db.String(255), nullable=False, unique=True)
    telephone = db.Column(db.String(255))

    administrators = db.relationship(
        "User",
        secondary=organ_administrators,
        backref=db.backref("organs_administered", lazy=True),
    )

    def __init__(
        self,
        *,
        name: str,
        cnpj: str,
        address: Optional[str] = None,
        email: str,
        telephone: Optional[str] = None,
    ):
        self.name = name
        self.cnpj = cnpj
        self.address = address
        self.email = email
        self.telephone = telephone
