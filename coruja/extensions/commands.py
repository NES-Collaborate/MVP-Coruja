from random import choices
from string import ascii_lowercase

from bcrypt import gensalt, hashpw
from flask import Flask

from ..extensions.database import db
from ..models import User


def init_database():
    print("Creating tables...")

    db.drop_all()
    db.create_all()
    db.session.commit()

    print("Tables Created\n")


def create_admin():
    print("Creating admin user...")

    password = "".join(choices(ascii_lowercase, k=10))
    hashed_password = hashpw(password.encode("utf-8"), gensalt())
    cpf = "00000000000"
    user = User(
        name="Administrador",
        cpf=cpf,
        password=hashed_password,
        email_professional="admin@coruja",
        is_adm=True,
    )

    db.session.add(user)
    db.session.commit()

    print("Admin User Created")
    print("-" * 15)
    print(f"Name: {user.name}")
    print(f"Password: {password}")
    print(f"CPF: {cpf}\n")


def init_app(app: Flask) -> None:
    @app.cli.command("initdb")
    def init_database_command():
        """Inicializa o banco de dados."""
        init_database()

    @app.cli.command("createsu")
    def create_admin_command():
        """Cria um usuário administrador."""
        create_admin()
