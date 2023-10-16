from flask import Flask

from .extensions import configurations


def create_app() -> Flask:
    """
    Cria e configura uma instância da aplicação Flask.
    Esta função inicializa uma instância da aplicação Flask, carrega as
    configurações e extensões necessárias.
    Retorna:
        - Flask: Uma instância da aplicação Flask configurada.
    """
    app = Flask(__name__)
    configurations.init_app(app)
    configurations.load_extensions(app)

    return app
