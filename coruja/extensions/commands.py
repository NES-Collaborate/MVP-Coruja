from random import choices
from string import ascii_lowercase

from flask import Flask

from ..extensions.database import db
from ..models import Permission, Role, User


def create_default_roles():
    print("Creating default roles...")
    permissions = [
        Permission(
            label="access_log",
            type="read",
            description="Acessar logs de acesso",
        ),
        Permission(
            label="configurations",
            type="read",
            description="Acessar configurações",
        ),
        Permission(
            label="configurations",
            type="write",
            description="Editar configurações",
        ),
        Permission(label="organ", type="create", description="Criar Órgãos"),
        Permission(label="organ", type="read", description="Acessar Órgãos"),
        Permission(label="organ", type="update", description="Editar Órgãos"),
        Permission(label="organ", type="delete", description="Deletar Órgãos"),
        Permission(
            label="institution",
            type="create",
            description="Criar Instituições",
        ),
        Permission(
            label="institution",
            type="read",
            description="Acessar Instituições",
        ),
        Permission(
            label="institution",
            type="update",
            description="Editar Instituições",
        ),
        Permission(
            label="institution",
            type="delete",
            description="Deletar Instituições",
        ),
        Permission(label="unit", type="create", description="Criar unidades"),
        Permission(label="unit", type="read", description="Acessar unidades"),
        Permission(label="unit", type="update", description="Editar unidades"),
        Permission(
            label="unit", type="delete", description="Deletar unidades"
        ),
    ]
    db.session.add_all(permissions)
    db.session.commit()

    admin_role = Role(name="admin", permissions=permissions)
    db.session.add(admin_role)
    db.session.commit()

    user_role = Role(name="user")
    db.session.add(user_role)
    db.session.commit()

    print("Default Roles Created\n")


def init_database():
    print("Creating tables...")

    db.drop_all()
    db.create_all()
    db.session.commit()

    create_default_roles()

    print("Tables Created\n")


def create_admin():
    print("Creating admin user...")

    password = "".join(choices(ascii_lowercase, k=10))
    cpf = "00000000000"

    user = User(
        name="Administrador",
        cpf=cpf,
        password=password,
        email_professional="admin@coruja",
        role=Role.query.filter_by(name="admin").first(),
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
    def _():
        """Inicializa o banco de dados."""
        init_database()

    @app.cli.command("createsu")
    def _():
        """Cria um usuário administrador."""
        create_admin()
