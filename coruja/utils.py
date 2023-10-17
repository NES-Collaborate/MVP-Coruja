from typing import Any, Dict, List

from flask_wtf import FlaskForm
from sqlalchemy.orm import aliased

from .extensions.database import db
from .models import Analysis, Organ, User, organ_administrators


def form_to_dict(form: FlaskForm) -> Dict[Any, Any]:
    _new_form = {}
    for atributte in dir(form):
        if callable(getattr(form, atributte)) or atributte.startswith("__"):
            continue

        _new_form[atributte] = getattr(form, atributte)

    return _new_form


class DatabaseManager:
    def __init__(self):
        self.__db = db

    def get_organs_by_user_id(self, user_id: int) -> List[Organ]:
        """
        Obtém órgãos associados a um usuário com base em seu ID.

        Params:
            user_id (int): O ID do usuário a ser pesquisado.

        Return:
            list[Organ]: Uma lista de objetos Organ associados ao usuário
                especificado.
        """
        organ_admin_alias = aliased(organ_administrators)

        return (
            Organ.query.join(
                organ_admin_alias,
                Organ.id == organ_admin_alias.c.organ_id,
            )
            .filter(organ_admin_alias.c.user_id == user_id)
            .all()
        )

    def get_analysis_by_id(
        self, analysis_id: int, or_404: bool = True
    ) -> Analysis:
        """Obtém uma análise com base em seu ID

        Args:
            analysis_id (int): O ID da análise
            or_404 (bool, optional): Se True, caso não exista uma análise com o ID
                especificado, `abort(404)`. Defaults to True.

        Returns:
            Analysis: A análise com o ID especificado
            None: Caso não exista uma análise com o ID especificado
        """
        analysis = (
            Analysis.query.filter_by(id=analysis_id).first_or_404(
                "Análise não encontrada com o ID especificado ({})".format(
                    analysis_id
                )
            )
            if or_404
            else Analysis.query.filter_by(id=analysis_id).first()
        )
        return analysis

    def get_user_by_id(self, user_id: int, or_404: bool = True) -> User:
        """Obtém um usuário com base em seu ID

        Args:
            user_id (int): O ID do usuário
            or_404 (bool, optional): Se True, caso não exista um usuário com o ID
                especificado, `abort(404)`. Defaults to True.

        Returns:
            User: O usuário com o ID especificado
        """
        user = (
            User.query.filter_by(id=user_id).first_or_404(
                "Usuário com o ID especificado ({}) não foi encontrado".format(
                    user_id
                )
            )
            if or_404
            else User.query.filter_by(id=user_id).first()
        )
        return user

    def create_analysis(self, **kwargs) -> Analysis:
        """
        Cria uma nova análise e atribui administradores a ela.

        Args:
            description (str): A descrição da análise.
            administrators (List[int]): Lista de IDs dos administradores.

        Returns:
            Analysis: O objeto de análise recém-criado.
        """
        administrators = kwargs.pop("administrators", [])
        new_analysis = Analysis(description=kwargs.pop("description", None))

        for admin_id in administrators:
            admin = self.get_user_by_id(admin_id)
            new_analysis.add_administrator(admin, commit_changes=False)

        self.__db.session.add(new_analysis)
        self.__db.session.commit()

        return new_analysis

    def add_organ(self, **kwargs) -> None:
        administrators = kwargs.pop("administrators", [])
        organ = Organ(**kwargs)

        self.__db.session.add(organ)
        self.__db.session.commit()

        organ.administrators.extend(administrators)

        self.__db.session.commit()
        self.__db.session.commit()

    def is_organ_administrator(self, user: User | Any) -> bool:
        organ_admin = aliased(organ_administrators)

        organs = (
            Organ.query.join(
                organ_admin,
                Organ.id == organ_admin.c["organ_id"],
            )
            .filter(organ_admin.c["user_id"] == user.id)
            .first()
        )

        return bool(organs)


database_manager = DatabaseManager()
