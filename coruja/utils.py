from typing import Any, Dict, List, Optional, overload

from flask_wtf import FlaskForm
from sqlalchemy.orm import aliased

from .extensions.database import db
from .models import (
    Active,
    ActiveScore,
    Analysis,
    AnalysisRisk,
    AnalysisVulnerability,
    Institution,
    Organ,
    Unit,
    User,
    institution_administrators,
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

    def get_organs(self, user_id: int) -> List[Organ]:
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

    def get_organ(
        self,
        organ_id: int,
        or_404: bool = True,
    ) -> Organ | None:
        """Obtém um orgão com base em seu ID.

        Args:
            organ_id (int): O ID do orgão.
            or_404 (bool, optional): Se True, caso não exista um orgão
                com o ID especificado, `abort(404)`. O padrão é True.

        Returns:
            Organ: O orgão com o ID especificado.
            None: Caso não exista um orgão com o ID especificado.
        """
        if or_404:
            message = "Orgão não encontrado"
            return Organ.query.filter_by(id=organ_id).first_or_404(message)

        return Organ.query.filter_by(id=organ_id).first()

    def update_organ(
        self,
        organ: Organ,
        form: Dict[str, Any],
    ) -> Organ:
        administrators: List[int] = form.pop("admin_ids", [])

        for key, value in form.items():
            setattr(organ, key, value)

        for administrator_id in administrators:
            administrator = self.get_user(administrator_id)
            organ.add_administrator(administrator)

        db.session.commit()

        return organ

    @overload
    def get_institutions(self, user_id: int) -> List[Institution]:
        """
        Obtém instituições associadas a um usuário com base em seu ID.

        Params:
            user_id (int): O ID do usuário a ser pesquisado.

        Return:
            list[Institution]: Uma lista de objetos Institution associados ao
                usuário especificado.
        """
        ...

    @overload
    def get_institutions(
        self,
        user_id: int,
        *,
        organ_id: int,
    ) -> List[Institution]:
        """
        Obtém instituições associadas a um usuário com base em seu ID
        e que estejam associados a um órgão.

        Params:
            user_id (int): O ID do usuário a ser pesquisado.
            organ_id (int): O ID do orgão a ser pesquisado.

        Return:
            list[Institution]: Uma lista de objetos Institution associados
                ao usuário e orgão especificado.
        """
        ...

    def get_institutions(
        self,
        user_id: int,
        *,
        organ_id: Optional[int] = None,
    ) -> List[Institution]:
        user_institution_alias = aliased(institution_administrators)

        if organ_id is None:
            return (
                Institution.query.join(
                    user_institution_alias,
                    Institution.id == user_institution_alias.c.institution_id,
                )
                .filter(user_institution_alias.c.user_id == user_id)
                .all()
            )

        return (
            Institution.query.join(
                user_institution_alias,
                Institution.id == user_institution_alias.c.institution_id,
            )
            .filter(
                user_institution_alias.c.user_id == user_id,
                user_institution_alias.c.organ_id == organ_id,
            )
            .all()
        )

    def get_institution(
        self, institution_id: int, or_404: bool = True
    ) -> Institution | None:
        """Obtém uma instituição com base em seu ID.

        Args:
            institution_id (int): O ID da Instituição.
            or_404 (bool, optional): Se True, caso não exista uma Instituição
                com o ID especificado, `abort(404)`. O padrão é True.

        Returns:
            Institution: A instituição com o ID especificado.
            None: Caso não exista uma Instituição com o ID especificado.

        Raises:
            NotFoundError: Se a instituição não foi encontrada e `or_404=True`
        """
        institution = (
            Institution.query.filter_by(id=institution_id).first_or_404(
                "Instituição não encontrada"
            )
            if or_404
            else Institution.query.filter_by(id=institution_id).first()
        )
        return institution

    def update_institution(
        self,
        institution: Institution,
        form: Dict[str, Any],
    ) -> Institution:
        administrators: List[int] = form.pop("admin_ids", [])

        for key, value in form.items():
            setattr(institution, key, value)

        for administrator_id in administrators:
            administrator = self.get_user(administrator_id)
            institution.add_administrator(administrator)

        db.session.commit()

        return institution

    def get_analysis(
        self,
        analysis_id: int,
        or_404: bool = True,
    ) -> Analysis | None:
        """Obtém uma análise com base em seu ID.

        Args:
            analysis_id (int): O ID da análise.
            or_404 (bool, optional): Se True, caso não exista uma análise
                com o ID especificado, `abort(404)`. O padrão é True.

        Returns:
            Analysis: A análise com o ID especificado.
            None: Caso não exista uma análise com o ID especificado.
        """
        analysis = (
            Analysis.query.filter_by(id=analysis_id).first_or_404(
                "Análise não encontrada"
            )
            if or_404
            else Analysis.query.filter_by(id=analysis_id).first()
        )
        return analysis  # type: ignore

    def get_unit(
        self,
        unit_id: int,
        or_404: bool = True,
    ) -> Unit | None:
        """Obtém uma unidade com base em seu ID.

        Args:
            unit_id (int): O ID da unidade.
            or_404 (bool, optional): Se True, caso não exista uma unidade
                com o ID especificado, `abort(404)`. O padrão é True.

        Returns:
            Unit: A unidade com o ID especificado.
            None: Caso não exista uma unidade com o ID especificado.

        Raises:
            NotFoundError: Se a unidade não foi encontrada e `or_404=True`
        """

        unit = (
            Unit.query.filter_by(id=unit_id).first_or_404(
                "Unidade não encontrada"
            )
            if or_404
            else Unit.query.filter_by(id=unit_id).first()
        )
        return unit

    def get_user(self, user_id: int, or_404: bool = True) -> User:
        """Obtém um usuário com base em seu ID

        Args:
            user_id (int): O ID do usuário
            or_404 (bool, optional): Se True, caso não exista um usuário com
                o ID especificado, `abort(404)`. Defaults to True.

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

    def add_analysis(self, **kwargs) -> Analysis:
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
            admin = self.get_user(admin_id)
            new_analysis.add_administrator(admin, commit_changes=False)

        self.__db.session.add(new_analysis)
        self.__db.session.commit()

        new_analysis_risk = AnalysisRisk(analysis_id=new_analysis.id)
        self.__db.session.add(new_analysis_risk)
        self.__db.session.commit()

        new_analysis_vulnerability = AnalysisVulnerability(
            analysis_id=new_analysis.id
        )
        self.__db.session.add(new_analysis_vulnerability)
        self.__db.session.commit()

        return new_analysis

    def update_analysis(
        self,
        analysis_id: int,
        description: str | None,
        administrators: List[int],
        experts: List[int],
    ) -> Analysis | None:
        """Atualiza os dados de uma análise com base em seu ID

        Args:
            analysis_id (int): ID da análise
            description (str): Nova descrição da análise
            administrators (List[int]): Nova lista de IDs dos administradores
            experts (List[int]): Nova lista de IDs dos especialistas

        Returns:
            Analysis: O objeto de análise atualizado
            None: Caso não exista uma analise com o ID especificado
        """
        analysis = self.get_analysis(analysis_id)
        if not analysis:
            return None
        analysis.description = description
        analysis.administrators = []
        analysis.experts = []

        for admin_id in administrators:
            admin = self.get_user(admin_id)
            analysis.add_administrator(admin, commit_changes=False)

        for expert_id in experts:
            expert = self.get_user(expert_id)
            analysis.add_expert(expert, commit_changes=False)

        db.session.commit()
        return analysis

    def get_actives_by_analysis(
        self,
        analysis: Analysis,
        with_average_scores: bool = True,
    ) -> List[Active]:
        """Obtém lista de ativos de uma determinada análise (ou seja, lista
        de ativos de uma análise de risco que está relacionada com a Análise
        especificada).

        Args:
            analysis (Analysis): Análise
            with_average_scores (bool, optional): Se True, inclui as médias
                dos scores dos ativos. Defaults to True.

        Returns:
            List[Active]: Lista de ativos.
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
            administrator = self.get_user(administrator_id)
            organ.add_administrator(administrator)

    def add_institution(self, **kwargs) -> Institution:
        """Adiciona uma instituição ao banco de dados e atribui administradores
        especificados a ela.

        Args:
            **kwargs (dict): Argumentos de palavra-chave contendo os atributos
                da instituição a ser adicionada e os IDs dos administradores.
            administrators (List[int]): Lista de IDs dos administradores

        Returns:
            Institution: A instituição adicionada ao banco de dados.
        """

        administrators = kwargs.pop("administrators", [])
        institution = Institution(**kwargs)

        self.__db.session.add(institution)
        self.__db.session.commit()

        for administrator_id in administrators:
            administrator = self.get_user(administrator_id)
            institution.add_administrator(administrator, commit_changes=False)

        self.__db.session.commit()
        return institution

    def is_organ_administrator(self, user: User | Any) -> bool:
        # TODO: implementar verificação de permission pela role
        role = user.role
        if not role:
            return False
        return role.name == "admin"

    def get_analysis_risk(
        self, analysis_risk_id: int, or_404: bool = True
    ) -> AnalysisRisk | None:
        """Obtém uma analise de risco por ID

        Args:
            analysis_risk_id (int): ID da analise
            or_404 (bool, optional): Se True, abort(404) caso não exista uma analise de
                risco com o ID especificado. Defaults to True

        Returns:
            AnalysisRisk: O objeto de analise
            None: Caso não exista uma analise de risco com o ID especificado

        Raises:
            NotFoundError: Se `or_404=True` e a analise de risco não foi encontrada
        """
        analysis_risk = (
            AnalysisRisk.query.filter_by(id=analysis_risk_id).first_or_404(
                "Análise de Risco não encontrada"
            )
            if or_404
            else AnalysisRisk.query.filter_by(id=analysis_risk_id).first()
        )

        return analysis_risk

    def get_analysis_vulnerability(
        self, analysis_vulnerability_id: int, or_404: bool = True
    ) -> AnalysisVulnerability | None:
        """Obtém uma analise de vulnerabilidade por ID

        Args:
            analysis_vulnerability_id (int): ID da analise de vulnerabilidade
            or_404 (bool, optional): Se True, abort(404) caso não exista uma analise de vulnerabilidade com o ID especificado. Defaults to True

        Returns:
            AnalysisVulnerability: O objeto de analise de vulnerabilidade
            None: Caso não exista uma analise de vulnerabilidade com o ID especificado

        Raises:
            NotFoundError: Se `or_404=True` e a analise de vulnerabilidade não foi encontrada
        """
        analysis_vulnerability = (
            AnalysisVulnerability.query.filter_by(
                id=analysis_vulnerability_id
            ).first_or_404("Análise de Vulnerabilidade não encontrada")
            if or_404
            else AnalysisVulnerability.query.filter_by(
                id=analysis_vulnerability_id
            ).first()
        )
        return analysis_vulnerability


database_manager = DatabaseManager()
