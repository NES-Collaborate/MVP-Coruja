from typing import Optional

from ..extensions.database import db
from .configurations import BaseTable
from .relationships import institution_administrators, institution_units
from .units import Unit
from .users import User


class Institution(BaseTable):
    name = db.Column(db.String(255), nullable=False)
    cnpj = db.Column(db.String(255), nullable=False, unique=True)
    address = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    telephone = db.Column(db.String(255), nullable=False, unique=True)
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

    def add_administrator(self, user: User, commit_changes: bool = True):
        """Adiciona um administrador a uma instituição

        Args:
            user (User): Usuário a ser adicionado
            commit_changes (bool, optional): Se True, salva as alterações no banco.
        """
        permissions = self.create_permissions()
        if not self.administrators:
            self.administrators = []

        self.administrators.append(user)
        for permission in permissions:
            user.add_permission(permission)

        if commit_changes:
            db.session.commit()

    def add_unit(self, unit: Unit):
        """Adiciona uma unidade à lista de unidades relacionadas à uma instituição

        Args:
            unit (Unit): Unidade a ser adicionada
        """
        if not self.units:
            self.units = []

        self.units.append(unit)

        db.session.commit()
