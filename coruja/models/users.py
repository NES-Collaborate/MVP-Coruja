import json
from datetime import datetime
from typing import List, Optional

from bcrypt import checkpw, gensalt, hashpw
from flask_login import UserMixin

from ..extensions.database import db
from .configurations import BaseTable
from .permissions import Permission
from .relationships import user_permissions


class User(BaseTable, UserMixin):
    name = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(11), nullable=False, unique=True)
    password = db.Column(db.String(180), nullable=False)
    email_personal = db.Column(db.String(255))  # , nullable=True, unique=True
    email_professional = db.Column(db.String(255), nullable=False, unique=True)
    address = db.Column(db.String(255))
    _telephones = db.Column(db.String)
    title = db.Column(db.String(255))
    last_seen = db.Column(db.DateTime)
    permissions: db.Mapped[List[Permission]] = db.relationship(  # type: ignore
        "Permission",
        secondary=user_permissions,
        backref=db.backref("users", lazy=True),
    )

    # Permitir várias linhas com valor nulo
    __table_args__ = (
        db.UniqueConstraint("email_personal", name="uq_email_personal"),
    )

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
    ):
        _password = hashpw(password.encode("utf-8"), gensalt())
        self.password = _password.decode("utf-8")

        self.name = name
        self.cpf = cpf
        self.email_personal = email_personal
        self.email_professional = email_professional
        self.address = address
        self.title = title
        self.last_seen = last_seen

    @property
    def telephones(self):
        return json.loads(self._telephones) if self._telephones else []

    @property
    def cpf_censored(self) -> str:
        return self.__censor_cpf(self.cpf)

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
        self,
        filter_params: Optional[list] = [],
        censor_cpf: bool = True,
    ) -> dict:
        """Retorna um dicionário com os atributos da classe.

        Args:
            filter_params (Optional[list], optional): Especifica os campos que
                devem ser retornados, quando vazio retorna todos. O padrão é [].
            censor_cpf (bool, optional): Se True, censura o CPF. O padrão é True.

        Returns:
            dict: Dicionário com os atributos da classe.
        """
        result = {}
        for column in self.__table__.columns:  # type: ignore
            if filter_params and column.name in filter_params:
                if censor_cpf and column.name == "cpf":
                    result[column.name] = self.__censor_cpf(
                        getattr(self, column.name)
                    )
                else:
                    result[column.name] = getattr(self, column.name)

        return result

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

    def add_permission(
        self, permission: Permission, commit_changes: bool = True
    ) -> None:
        if not self.permissions:
            self.permissions = []

        self.permissions.append(permission)

        if commit_changes:
            db.session.commit()
