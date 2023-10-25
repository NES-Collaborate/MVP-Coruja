import ipdb
from flask_wtf import FlaskForm
from wtforms import (
    EmailField,
    FieldList,
    HiddenField,
    PasswordField,
    StringField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Optional,
    Regexp,
    ValidationError,
)

from coruja.models.organs import Organ

from .utils import UniqueTable


def validate_cpf(form, field):
    """
    Valida o número de CPF inserido no formulário.
    Parameters:
        - form (FlaskForm): O formulário FlaskForm atual.
        - field (StringField): O campo de CPF no formulário.
    Raise:
        - ValidationError: Se o CPF não for válido (não numérico ou não
            tem 11 dígitos).
    """
    cpf = field.data
    if not cpf.isnumeric() or len(cpf) != 11:
        raise ValidationError("CPF Inválido")


class LoginForm(FlaskForm):
    """
    Formulário de login.
    Fields:
        - cpf (StringField): O campo para inserir o CPF do usuário.
        - password (PasswordField): O campo para inserir a senha do usuário.
        - csrf_token (HiddenField): O campo oculto para proteção CSRF.
    """

    cpf = StringField(
        label="CPF",
        validators=[DataRequired("Preencha esse campo"), validate_cpf],
        description="Somente Números",
    )
    password = PasswordField(
        label="Senha", validators=[DataRequired("Preencha esse campo")]
    )
    submit = SubmitField(label="Entrar")
    csrf_token = HiddenField()


class OrganForm(FlaskForm):
    """
    Formulário para criar um órgão.

    Fields:
        - csrf_token (HiddenField): O campo oculto para proteção CSRF.
        - name (str): O campo para inserir o nome do órgão.
        - cnpj (str): O campo para inserir o CNPJ do órgão.
        - address (str): O campo para inserir o endereço do órgão.
        - email (str): O campo para inserir o e-mail do órgão.
        - telephone (str): O campo para inserir o telefone do órgão.
    """

    csrf_token = HiddenField()
    name = StringField(
        "Nome", validators=[DataRequired("Este campo é obrigatório")]
    )
    cnpj = StringField(
        "CNPJ",
        validators=[
            DataRequired("Este campo é obrigatório"),
            Regexp(
                r"^\d{2}.\d{3}.\d{3}\/\d{4}-\d{2}$",
                message="Insira um CNPJ válido",
            ),
            UniqueTable(
                table=Organ,
                message="Este CNPJ já está cadastrado",
            ),
        ],
    )
    address = StringField("Endereço")
    email = EmailField(
        "E-mail",
        validators=[
            DataRequired("Este campo é obrigatório"),
            Email("Digite um endereço de e-mail válido"),
            UniqueTable(
                table=Organ,
                message="Este e-mail já está cadastrado",
            ),
        ],
    )
    telephone = StringField(
        "Telefone",
        validators=[
            DataRequired("Este campo é obrigatório"),
            Regexp(
                r"^(\(\d{2,3}\) \d{4,5}-\d{4}|\d{10,11})$",
                message="Formato de telefone inválido",
            ),
            UniqueTable(
                table=Organ,
                message="Este telefone já está cadastrado",
            ),
        ],
    )
    admin_ids = FieldList(HiddenField(), min_entries=1)
    submit = SubmitField("Criar orgão")

    def __init__(self, *args, **kwargs):
        self.is_edit = kwargs.pop("is_edit", False)
        self.obj = kwargs.get("obj", None)

        super().__init__(*args, **kwargs)


class InstitutionForm(FlaskForm):
    """
    Formulário para criar uma instituição.

    Fields:
        - csrf_token (HiddenField): O campo oculto para proteção CSRF.
        - name (str): O campo para inserir o nome da instituição.
        - address (str): O campo para inserir o endereço da instituição.
        - description (str): O campo para inserir a descrição da instituição.
        - cnpj (str, optional): O campo para inserir o CNPJ da instituição.
    """

    csrf_token = HiddenField()
    name = StringField(
        "Nome", validators=[DataRequired("Este campo é obrigatório")]
    )
    address = StringField("Endereço")
    cnpj = StringField(
        "CNPJ",
        validators=[
            Optional(),
            Regexp(
                r"^\d{2}.\d{3}.\d{3}\/\d{4}-\d{2}$",
                message="Insira um CNPJ válido",
            ),
        ],
    )
    email = EmailField(
        "E-mail",
        validators=[
            DataRequired("Este campo é obrigatório"),
            Email("Digite um endereço de e-mail válido"),
        ],
    )
    telephone = StringField(
        "Telefone",
        validators=[
            DataRequired("Este campo é obrigatório"),
            Regexp(
                r"^\(\d{2,3}\) \d{4,5}-\d{4}$",
                message="Formato de telefone inválido. Use (99) 99999-9999.",
            ),
        ],
    )
    admin_ids = FieldList(HiddenField(), min_entries=1)
    submit = SubmitField("Criar instituição")


class UnitForm(FlaskForm):
    """
    Formulário para criar uma Unidade.

    Fields:
        - csrf_token (HiddenField): O campo oculto para proteção CSRF.
        - name (str): O campo para inserir o nome da unidade.
        - address (str): O campo para inserir o endereço da unidade.
        - description (str, optional): O campo para inserir a descrição da unidade.
    """

    csrf_token = HiddenField()
    name = StringField(
        "Nome", validators=[DataRequired("Este campo é obrigatório")]
    )
    address = StringField(
        "Endereço", validators=[DataRequired("Este campo é obrigatório")]
    )
    description = StringField("Descrição")
    admin_ids = FieldList(HiddenField(), min_entries=1)
    submit = SubmitField("Criar instituição")


class AnalysisForm(FlaskForm):
    """
    Formulário para criar / editar uma análise.
    Fields:
        - csrf_token (HiddenField): O campo oculto para proteção CSRF.
        - description (str): O campo para inserir a descrição da análise.
    """

    csrf_token = HiddenField()
    description = StringField("Descrição")
    admin_ids = FieldList(HiddenField(), min_entries=1)
    expert_ids = FieldList(HiddenField())
    submit = SubmitField("Submeter")
