from functools import reduce
from random import choices
from string import ascii_lowercase

from flask import Flask

from ..extensions.database import db
from ..models import Permission, Role, User
from ..utils import create_and_commit_role


def create_default_roles():
    """Cria os 'cargos' padrões dos usuários"""
    print("Creating default roles...")

    # Permissões de configurações
    config_permissions = [
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
    ]

    # Permissões de órgãos
    organ_permissions = [
        Permission(label="organ", type="create", description="Criar órgãos"),
        Permission(label="organ", type="read", description="Acessar órgãos"),
        Permission(label="organ", type="update", description="Editar órgãos"),
    ]

    # Permissões de instituições
    institution_permisssions = [
        Permission(
            label="institution",
            type="create",
            description="Criar instituições",
        ),
        Permission(
            label="institution",
            type="read",
            description="Acessar instituições",
        ),
        Permission(
            label="institution",
            type="update",
            description="Editar instituições",
        ),
    ]

    # Permissões de unidades
    unit_permissions = [
        Permission(label="unit", type="create", description="Criar unidades"),
        Permission(label="unit", type="read", description="Acessar unidades"),
        Permission(label="unit", type="update", description="Editar unidades"),
    ]

    # Permissões de análise
    analysis_permissions = [
        Permission(
            label="analysis",
            type="create",
            description="Criar análises",
        ),
        Permission(
            label="analysis",
            type="read",
            description="Acessar análises",
        ),
        Permission(
            label="analysis",
            type="update",
            description="Editar análises",
        ),
    ]

    # Permissões de ativos
    active_permissions = [
        Permission(
            label="active",
            type="create",
            description="Criar ativos",
        ),
        Permission(
            label="active",
            type="read",
            description="Acessar ativos",
        ),
        Permission(
            label="active",
            type="update",
            description="Editar ativos",
        ),
    ]

    # Permissões de usuários
    user_permissions = [
        Permission(
            label="user",
            type="create",
            description="Criar usuários",
        ),
        Permission(
            label="user",
            type="read",
            description="Acessar usuários",
        ),
        Permission(
            label="user",
            type="update",
            description="Editar usuários",
        ),
    ]

    all_permissions = [
        config_permissions,
        organ_permissions,
        institution_permisssions,
        unit_permissions,
        analysis_permissions,
        user_permissions,
        active_permissions,
    ]

    for permission in all_permissions:
        db.session.add_all(permission)

    all_permissions = reduce(lambda x, y: x + y, all_permissions)

    # Adiciona o cargo de administrador
    create_and_commit_role("admin", all_permissions)

    # Remove e adiciona permissões de órgãos e instituições
    organ_admin_permisssions = organ_permissions.copy() + user_permissions
    organ_admin_permisssions.remove(organ_permissions[0])
    organ_admin_permisssions.append(institution_permisssions[0])
    # Adiciona o cargo de administrador de órgãos
    create_and_commit_role("organ_admin", organ_admin_permisssions)

    # Remove e adiciona permissões de instituições e unidades
    institution_admin_permisssions = (
        institution_permisssions.copy() + user_permissions
    )
    institution_admin_permisssions.remove(institution_permisssions[0])
    institution_admin_permisssions.append(unit_permissions[0])
    # Adiciona o cargo de administrador de instituições
    create_and_commit_role("institution_admin", institution_admin_permisssions)

    # Remove e adiciona permissões de unidades e análises
    unit_admin_permissions = unit_permissions.copy() + user_permissions
    unit_admin_permissions.remove(unit_permissions[0])
    unit_admin_permissions.append(analysis_permissions[0])
    # Adiciona o cargo de administrador de unidades
    create_and_commit_role("unit_admin", unit_admin_permissions)

    # Adiciona de permissões de análises
    analysis_admin_permissions = analysis_permissions.copy() + user_permissions
    analysis_admin_permissions.remove(analysis_permissions[0])
    analysis_admin_permissions.extend(active_permissions)
    # Adiciona o cargo de administrador de unidades
    create_and_commit_role("analysis_admin", unit_admin_permissions)

    # Adiciona o cargo de usuário visualizador
    create_and_commit_role("user", [user_permissions[1]])

    print("Default Roles Created\n")


def init_database():
    """Cria as tabelas do banco de dados e alimenta com dados padrões"""
    print("Creating tables...")

    db.drop_all()
    db.create_all()
    db.session.commit()

    create_default_roles()

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
    @app.cli.command("createroles")
    def _():
        """Cria as regras de acesso padrão."""
        create_default_roles()

    @app.cli.command("createsu")
    def _():
        """Cria um usuário administrador."""
        create_admin()
