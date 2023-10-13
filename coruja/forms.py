from flask_wtf import FlaskForm
from wtforms import HiddenField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError


def validate_cpf(form, field):
    cpf = field.data
    if not cpf.isnumeric() or len(cpf) != 11:
        raise ValidationError("CPF Inválido")


class LoginForm(FlaskForm):
    cpf = StringField(
        label="CPF",
        validators=[DataRequired(), Length(min=11, max=11), validate_cpf],
        description="Somente Números",
    )
    password = PasswordField(label="Senha", validators=[DataRequired()])
    submit = SubmitField(label="Entrar")
    csrf_token = HiddenField()


class OrgaoForm(FlaskForm):
    csrf_token = HiddenField()
    name = StringField("Nome", validators=[DataRequired()])
    cnpj = StringField("CNPJ", validators=[DataRequired()])
    address = StringField("Endereço")
    email = StringField("E-mail", validators=[DataRequired()])
    telephone = StringField("Telefone", validators=[DataRequired()])
    submit = SubmitField("Criar Orgão")
