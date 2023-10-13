import json
from datetime import datetime
from typing import Optional

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions.database import db
from .configurations import BaseTable


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
    is_administrator = db.Column(db.Boolean, default=False)

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
        is_administrator: bool = False,
    ):
        self.name = name
        self.cpf = cpf
        self.password = generate_password_hash(password)
        self.email_personal = email_personal
        self.email_professional = email_professional
        self.address = address
        self.title = title
        self.last_seen = last_seen
        self.is_administrator = is_administrator

    @property
    def telephones(self):
        return json.loads(self._telephones) if self._telephones else []

    @telephones.setter
    def telephones(self, value):
        self._telephones = json.dumps(value)

    @telephones.deleter
    def telephones(self):
        del self._telephones

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)
