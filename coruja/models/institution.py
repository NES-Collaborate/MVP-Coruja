from typing import Optional

from ..extensions.database import db
from .configurations import BaseTable

institution_administrators = db.Table(
    "institution_administrators",
    db.Column("institution_id", db.Integer, db.ForeignKey("institution.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
)


class Institution(BaseTable):
    name = db.Column(db.String(255), nullable=False)
    cnpj = db.Column(db.String(255), unique=True)
    address = db.Column(db.String(255))
    email = db.Column(db.String(255), nullable=False, unique=True)
    telephone = db.Column(db.String(255))

    administrators = db.relationship(
        "User",
        secondary=institution_administrators,
        backref=db.backref("institutions_administered", lazy="dynamic"),
    )

    def __init__(
        self,
        *,
        name: str,
        cnpj: str,
        email: str,
        address: Optional[str] = None,
        telephone: Optional[str] = None,
    ):
        self.name = name
        self.cnpj = cnpj
        self.address = address
        self.email = email
        self.telephone = telephone
