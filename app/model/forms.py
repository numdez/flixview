from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, EmailField, SelectField, validators, DateField, RadioField, TextAreaField, FileField
from wtforms.validators import DataRequired, InputRequired, Optional

# Login
class LoginForm(FlaskForm):
    email = EmailField("E-mail", validators=[DataRequired()])
    senha = PasswordField("Senha", validators=[DataRequired()])
    next = StringField()

class AddUsuarioForm(FlaskForm):
    nome_usuario = StringField("Nome do usuário")
    email_usuario = EmailField("E-mail")
    senha_usuario = PasswordField("Senha")
    tipo_usuario = SelectField("Tipo")

class UpdateUsuarioForm(FlaskForm):
    nome_usuario = StringField("Nome do usuário")
    email_usuario = EmailField("E-mail")
    senha_usuario = PasswordField("Senha")
    tipo_usuario = SelectField("Tipo")