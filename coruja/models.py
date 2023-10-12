from . import db, session
from datetime import datetime
from sqlalchemy import event
from flask_login import UserMixin
import json
from bcrypt import checkpw


class BaseTable(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def on_update(self):
        change = Change(
            object_old=self.__dict__["_original_state"]
            if "_original_state" in self.__dict__
            else None,
            object_new=self.__dict__,
            user_id=session["user_id"],
        )

        db.session.add(change)
        db.session.commit()


@event.listens_for(BaseTable, "before_update")
def before_update(mapper, connection, target):
    target.on_update()


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
    is_adm = db.Column(db.Boolean, default=False)

    def check_password(self, password: str):
        return checkpw(password.encode("utf-8"), self.password)

    @property
    def telephones(self):
        return json.loads(self._telephones) if self._telephones else []

    @telephones.setter
    def telephones(self, value):
        self._telephones = json.dumps(value)

    @telephones.deleter
    def telephones(self):
        del self._telephones


orgao_administrators = db.Table(
    "orgao_administrators",
    db.Column("orgao_id", db.Integer, db.ForeignKey("orgao.id"), primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
)


class Orgao(BaseTable):
    name = db.Column(db.String(255), nullable=False)
    cnpj = db.Column(db.String(255), nullable=False, unique=True)
    address = db.Column(db.String(255))
    email = db.Column(db.String(255), nullable=False, unique=True)
    telephone = db.Column(db.String(255))
    administrators = db.relationship(
        "User",
        secondary=orgao_administrators,
        backref=db.backref("orgaos_admin", lazy=True),
    )


administradores_instituicao = db.Table(
    "administradores_instituicao",
    db.Column("instituicao_id", db.Integer, db.ForeignKey("instituicao.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
)


class Instituicao(BaseTable):
    name = db.Column(db.String(255), nullable=False)
    cnpj = db.Column(db.String(255), unique=True)
    address = db.Column(db.String(255))
    email = db.Column(db.String(255), nullable=False, unique=True)
    telephone = db.Column(db.String(255))
    administrators = db.relationship(
        "User",
        secondary=administradores_instituicao,
        backref=db.backref("instituicoes_administradas", lazy="dynamic"),
    )


administradores_analise = db.Table(
    "administradores_analise",
    db.Column("analise_id", db.Integer, db.ForeignKey("analise.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
)


class Analise(BaseTable):
    description = db.Column(db.String)
    administrators = db.relationship(
        "User",
        secondary=administradores_analise,
        backref=db.backref("analises_administradas", lazy="dynamic"),
    )


class Ativo(BaseTable):
    title = db.Column(db.String(255))
    description = db.Column(db.String)
    analise_id = db.Column(db.Integer, db.ForeignKey("analise.id"))
    analise = db.relationship("Analise", backref="ativos", lazy=True)


class AtivoScore(BaseTable):
    substitibilidade = db.Column(db.Integer, nullable=False, default=0)
    custo_reposicao = db.Column(db.Integer, nullable=False, default=0)
    essenciabilidade = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref="ativos_scores", lazy=True)
    ativo_id = db.Column(db.Integer, db.ForeignKey("ativo.id"), nullable=False)
    ativo = db.relationship("Ativo", backref="ativos_scores", lazy=True)


class Ameaca(BaseTable):
    title = db.Column(db.String(255))
    description = db.Column(db.String)
    ativo_id = db.Column(db.Integer, db.ForeignKey("ativo.id"))
    ativo = db.relationship("Ativo", backref="ameacas", lazy=True)


class AcaoAdversa(BaseTable):
    title = db.Column(db.String(255))
    description = db.Column(db.String)
    ameaca_id = db.Column(db.Integer, db.ForeignKey("ameaca.id"))
    ameaca = db.relationship("Ameaca", backref="acoes_adversas", lazy=True)


class AcaoAdversaScore(BaseTable):
    motivacao = db.Column(db.Integer, default=0)
    capacidade = db.Column(db.Integer, default=0)
    acessibilidade = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref="acoes_adversas_scores", lazy=True)
    acao_adversa_id = db.Column(
        db.Integer, db.ForeignKey("acao_adversa.id"), nullable=False
    )
    acao_adversa = db.relationship(
        "AcaoAdversa", backref="acoes_adversas_scores", lazy=True
    )


class VulnerabilityCategory(BaseTable):
    name = db.Column(db.String(255), nullable=False)


class VulnerabilitySubCategory(BaseTable):
    name = db.Column(db.String(255), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("vulnerability_category.id"))
    category = db.relationship(
        "VulnerabilityCategory", backref="vulnerability_sub_categories", lazy=True
    )


class Vulnerability(BaseTable):
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String)
    sub_category_id = db.Column(
        db.Integer, db.ForeignKey("vulnerability_sub_category.id")
    )
    sub_category = db.relationship(
        "VulnerabilitySubCategory", backref="vulnerabilities", lazy=True
    )


class VulnerabilityScore(BaseTable):
    score = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref="vulnerability_scores", lazy=True)
    vulnerability_id = db.Column(
        db.Integer, db.ForeignKey("vulnerability.id"), nullable=False
    )
    vulnerability = db.relationship(
        "Vulnerability", backref="vulnerability_scores", lazy=True
    )


class Change(BaseTable):
    object_old = db.Column(db.JSON)
    object_new = db.Column(db.JSON)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref="changes", lazy=True)


class AccessLog(BaseTable):
    ip = db.Column(db.String(255))
    user_agent = db.Column(db.String(255))
    access_at = db.Column(db.DateTime)
    endpoint = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref="access_logs", lazy=True)
