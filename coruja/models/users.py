import json
from datetime import datetime
from typing import Optional

from bcrypt import checkpw, gensalt, hashpw
from flask_login import UserMixin

from ..extensions.database import db
from .configurations import BaseTable


class Permission(BaseTable):
    label = db.Column(db.String(255), nullable=False)
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

    def add_permission(
        self, permission: Permission, commit_changes: bool = False
    ) -> None:
        if not self.permissions:
            self.permissions = []

        self.permissions.append(permission)
        if commit_changes:
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
        """Verifica se a senha está correta

        Args:
            password (str): Senha a ser verificada

        Returns:
            bool: True se a senha estiver correta. False caso não.
        """
        return checkpw(password.encode("utf-8"), self.password.encode("utf-8"))

    def as_dict(
        self, filter_params: Optional[list] = [], censor_cpf: bool = True
    ) -> dict:
        """Retorna um dicionário com os atributos da classe

        Args:
            filter_params (Optional[list], optional): Especifica os campos que devem ser
                retornados, quando vazio retorna todos. Defaults to [].
            censor_cpf (bool, optional): Se True, censura o CPF. Defaults to True.

        Returns:
            dict: Dicionário com os atributos da classe
        """
        return {
            c.name: self.__censor_cpf(getattr(self, c.name))
            if c.name == "cpf" and censor_cpf
            else getattr(self, c.name)
            for c in self.__table__.columns
            if c.name in filter_params and filter_params
        }

    def __censor_cpf(self, cpf: str) -> str:
        """
        Censura um CPF, mantendo apenas os três primeiros e os dois últimos dígitos
        visíveis.

        Exemplo: Se o CPF for 123.456.789-09, ele se tornará 123.***.**9-09.

        Args:
            cpf (str): O CPF a ser censurado.

        Return:
            str: O CPF censurado.
        """
        return f"{cpf[:3]}.***.**{cpf[-3]}-{cpf[-2:]}"

    @property
    def cpf_censored(self) -> str:
        return self.__censor_cpf(self.cpf)
