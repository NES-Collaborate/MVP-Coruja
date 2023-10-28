from functools import reduce
from random import choices
from string import ascii_lowercase

from flask import Flask

from ..extensions.database import db
from ..models import Permission, User


def create_default_permissions():
    """Cria os 'cargos' padrões dos usuários"""
    print("Creating default permissions...")

    # Permissões de Administração
    config_permissions = [
        Permission(type="read", object_type="admin"),
        Permission(type="update", object_type="admin"),
        Permission(type="delete", object_type="admin"),
        Permission(type="create", object_type="admin"),
    ]

    # Permissões de usuários
    user_permissions = [
        Permission(type="create", object_type="user"),
        Permission(type="read", object_type="user"),
        Permission(type="update", object_type="user"),
        Permission(type="delete", object_type="user"),
    ]

    # Permissões de Organ
    organ_permissions = [
        Permission(type="create", object_type="organ"),
    ]

    all_permissions = [
        config_permissions,
        user_permissions,
        organ_permissions,
    ]

    for permission in all_permissions:
        db.session.add_all(permission)

    db.session.commit()

    all_permissions = reduce(lambda x, y: x + y, all_permissions)

    print("Default Permissions Created\n")


def init_database():
    """Cria as tabelas do banco de dados e alimenta com dados padrões"""
    print("Creating tables...")

    db.drop_all()
    db.create_all()
    db.session.commit()

    create_default_permissions()

    print("Tables Created\n")


def create_admin():
    """Cria um usuário administrador"""
    print("Creating admin user...")

    password = "".join(choices(ascii_lowercase, k=10))
    cpf = "00000000000"

    user = User(
        name="Administrador",
        cpf=cpf,
        password=password,
        email_professional="admin@coruja",
    )

    db.session.add(user)
    db.session.commit()

    permissions = Permission.query.all()
    for permission in permissions:
        user.add_permission(permission)

    db.session.commit()

    print("Admin User Created")
    print("-" * 15)
    print(f"Name: {user.name}")
    print(f"Password: {password}")
    print(f"CPF: {cpf}\n")


def init_app(app: Flask) -> None:
    @app.cli.command("createroles")
    def _():
        """Cria as regras de acesso padrão."""
        create_default_permissions()

    @app.cli.command("createsu")
    def _():
        """Cria um usuário administrador."""
        create_admin()
