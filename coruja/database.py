from . import db, app
from .models import User
from random import choices
from string import ascii_lowercase
from bcrypt import hashpw, gensalt


@app.cli.command("initdb")
def initdb_command():
    print("Creating tables...")
    db.drop_all()
    db.create_all()
    db.session.commit()
    print("Tables Created")


@app.cli.command("createsu")
def createsu_command():
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
    print(f"CPF: {cpf}")
