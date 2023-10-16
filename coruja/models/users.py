import json
from datetime import datetime
from typing import Optional

from bcrypt import checkpw, gensalt, hashpw
from flask_login import UserMixin

from ..extensions.database import db
from .configurations import BaseTable


class Permission(BaseTable):
    label = db.Column(db.String(255), nullable=False, unique=True)
    type = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)

    def __init__(self, *, label: str, type: str, description: str):
        """Permissão de acesso à funcionalidades gerais da aplicação

        Args:
            label (str): Nome da permissão
            type (str): Tipo de permissão (`create`, `read`, `update`, `delete`)
            description (str): Breve descrição sobre a permissão
        """
        self.label = label
        self.type = type
        self.description = description


permissions_roles = db.Table(
    "permissions_roles",
    db.Column("role_id", db.String, db.ForeignKey("role.id")),
    db.Column("permission_id", db.String, db.ForeignKey("permission.id")),
)


class Role(BaseTable):
    name = db.Column(db.String(255), nullable=False)
    permissions = db.relationship(
        "Permission",
        secondary=permissions_roles,
        backref=db.backref("roles", lazy=True),
    )

    def __init__(self, *, name: str, permissions: list = []):
        self.name = name

        for permission in permissions:
            self.add_permission(permission)

    def add_permission(self, permission: Permission) -> None:
        if not self.permissions:
            self.permissions = []

        self.permissions.append(permission)
        db.session.commit()


class User(BaseTable, UserMixin):
    name = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(11), nullable=False, unique=True)
    password = db.Column(db.String(180), nullable=False)
    email_personal = db.Column(db.String(255))
    email_professional = db.Column(db.String(255), nullable=False, unique=True)
    address = db.Column(db.String(255))
    _telephones = db.Column(db.String)
    title = db.Column(db.String(255))
    last_seen = db.Column(db.DateTime)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))

    role = db.relationship("Role", backref="users", lazy=True)

    def __init__(
        self,
        *,
        name: str,
        cpf: str,
        password: str,
        email_personal: Optional[str] = None,
        email_professional: str,
        address: Optional[str] = None,
        title: Optional[str] = None,
        last_seen: Optional[datetime] = None,
        role: Optional[Role] = None,
    ):
        self.name = name
        self.cpf = cpf
        self.password = hashpw(password.encode("utf-8"), gensalt()).decode(
            "utf-8"
        )
        self.email_personal = email_personal
        self.email_professional = email_professional
        self.address = address
        self.title = title
        self.last_seen = last_seen
        self.role = role or Role.query.filter_by(name="user").first()

    @property
    def telephones(self):
        return json.loads(self._telephones) if self._telephones else []

    @telephones.setter
    def telephones(self, value) -> None:
        self._telephones = json.dumps(value)

    @telephones.deleter
    def telephones(self) -> None:
        del self._telephones

    def check_password(self, password: str) -> bool:
        return checkpw(password.encode("utf-8"), self.password.encode("utf-8"))
