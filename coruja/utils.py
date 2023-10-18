from typing import Any, Dict, List

from flask_wtf import FlaskForm
from sqlalchemy.orm import aliased

from .extensions.database import db
from .models import (
    Active,
    ActiveScore,
    Analysis,
    AnalysisRisk,
    Organ,
    User,
    organ_administrators,
)


def form_to_dict(form: FlaskForm) -> Dict[Any, Any]:
    _new_form = {}
    for atributte in dir(form):
        if callable(getattr(form, atributte)) or atributte.startswith("_"):
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

    def get_organ_by_id(
        self, organ_id: int, or_404: bool = True
    ) -> Organ | None:
        """Obtém um órgão com base em seu ID

        Args:
            organ_id (int): O ID do órgão
            or_404 (bool, optional): Se True, caso não exista um organ com o ID especificado, `abort(404)`. Defaults to True.

        Returns:
            Organ: O objeto om o ID especificado
        """
        organ = (
            Organ.query.filter_by(id=organ_id).first_or_404(
                f"Orgão não encontrado com o ID especificado ({organ_id})"
            )
            if or_404
            else Organ.query.filter_by(id=organ_id).first()
        )

        return organ

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
        return analysis  # type: ignore

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
        return user  # type: ignore

    def create_analysis(self, **kwargs) -> Analysis:
        """
        Cria uma nova análise e atribui administradores a ela.
        Relacionado à esta anaĺise cria Análise de Risco e Análise de Vulnerabilidade

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

    def update_analysis(
        self,
        analysis_id: int,
        description: str | None,
        administrators: List[int],
        experts: List[int],
    ) -> Analysis:
        """Atualiza os dados de uma análise com base em seu ID

        Args:
            analysis_id (int): ID da análise
            description (str): Nova descrição da análise
            administrators (List[int]): Nova lista de IDs dos administradores
            experts (List[int]): Nova lista de IDs dos especialistas

        Returns:
            Analysis: O objeto de análise atualizado
        """
        analysis = self.get_analysis_by_id(analysis_id)
        analysis.description = description
        analysis.administrators = []
        analysis.experts = []

        for admin_id in administrators:
            admin = self.get_user_by_id(admin_id)
            analysis.add_administrator(admin, commit_changes=False)

        for expert_id in experts:
            expert = self.get_user_by_id(expert_id)
            analysis.add_expert(expert, commit_changes=False)

        db.session.commit()
        return analysis

    def get_actives_by_analysis(
        self, analysis: Analysis, with_average_scores: bool = True
    ) -> List[Active]:
        """Obtém lista de ativos de uma determinada análise (ou seja, lista de ativos de uma análise de risco que está relacionada com a Análise especificada).

        Args:
            analysis (Analysis): Análise
            with_average_scores (bool, optional): Se True, inclui as médias dos scores dos ativos. Defaults to True.

        Returns:
            List[Active]: Lista de ativos
        """
        analysis_risk = analysis.analysis_risk
        if not analysis_risk:
            return []
        actives = Active.query.filter_by(
            analysis_risk_id=analysis_risk.id
        ).all()
        if with_average_scores:
            for active in actives:
                active_scores: List[ActiveScore] = ActiveScore.query.filter_by(
                    active_id=active.id
                ).all()
                active.average_substitutability = sum(
                    score.substitutability for score in active_scores
                ) / len(active_scores)
                active.average_replacement_cost = sum(
                    score.replacement_cost for score in active_scores
                ) / len(active_scores)
                active.average_essentiality = sum(
                    score.essentiality for score in active_scores
                ) / len(active_scores)
        return actives

    def add_organ(self, **kwargs) -> None:
        """Adiciona um órgão ao banco de dados e atribui administradores
        especificados a ele.

        Args:
            **kwargs (dict): Argumentos de palavra-chave contendo os atributos
                do órgão a ser adicionado e os IDs dos administradores.
        """
        administrators = kwargs.pop("administrators", [])
        organ = Organ(**kwargs)

        self.__db.session.add(organ)
        self.__db.session.commit()

        for administrator_id in administrators:
            administrator = self.get_user_by_id(administrator_id)
            organ.add_administrator(administrator)

    def is_organ_administrator(self, user: User | Any) -> bool:
        # TODO: implementar verificação de permission pela role
        return user.role.name == "admin"

    def get_analysis_risk_by_id(
        self, analysis_risk_id: int, or_404: bool = True
    ) -> AnalysisRisk:
        """Obtém uma analise de risco por ID

        Args:
            analysis_risk_id (int): ID da analise
            or_404 (bool, optional): Se True, abort(404) caso não exista uma analise de risco com o ID especificado. Defaults to True

        Returns:
            AnalysisRisk: O objeto de analise
        """
        analysis_risk = AnalysisRisk.query.filter_by(
            id=analysis_risk_id
        ).first_or_404(
            "Análise de Risco não encontrada com o ID especificado ({})".format(
                analysis_risk_id
            )
            if or_404
            else AnalysisRisk.query.filter_by(id=analysis_risk_id).first()
        )

        return analysis_risk


database_manager = DatabaseManager()
