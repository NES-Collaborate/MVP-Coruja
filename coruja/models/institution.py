from typing import Optional

from ..extensions.database import db
from .configurations import BaseTable
from .units import Unit
from .users import User

institution_administrators = db.Table(
    "institution_administrators",
    db.Column("institution_id", db.Integer, db.ForeignKey("institution.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
)

institution_units = db.Table(
    "institution_units",
    db.Column(
        "institution_id",
        db.Integer,
        db.ForeignKey("institution.id"),
        primary_key=True,
    ),
    db.Column(
        "unit_id", db.Integer, db.ForeignKey("unit.id"), primary_key=True
    ),
)


class Institution(BaseTable):
    name = db.Column(db.String(255), nullable=False)
    cnpj = db.Column(db.String(255), unique=True)
    address = db.Column(db.String(255))
    email = db.Column(db.String(255), nullable=False, unique=True)
    telephone = db.Column(db.String(255))
    is_template = db.Column(db.Boolean, default=False)

    administrators = db.relationship(
        "User",
        secondary=institution_administrators,
        backref=db.backref("institutions_administered", lazy="dynamic"),
    )

    units = db.relationship(
        "Unit",
        secondary=institution_units,
        backref=db.backref("institutions", lazy="dynamic"),
    )

    def __init__(
        self,
        *,
        name: str,
        cnpj: str,
        email: str,
        address: Optional[str] = None,
        telephone: Optional[str] = None,
        is_template: Optional[bool] = False,
    ):
        self.name = name
        self.cnpj = cnpj
        self.address = address
        self.email = email
        self.telephone = telephone
        self.is_template = is_template

    def add_administrator(self, user: "User", commit_changes: bool = True):
        """Adiciona um administrador a uma instituição

        Args:
            user (User): Usuário a ser adicionado
            commit_changes (bool, optional): Se True, salva as alterações no banco.
        """
        if not self.administrators:
            self.administrators = []

        self.administrators.append(user)

        if commit_changes:
            db.session.commit()

    def add_unit(self, unit: Unit):
        if not self.units:
            self.units = []

        self.units.append(unit)

        db.session.commit()
