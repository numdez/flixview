from flask import Flask, session
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import config
from flask_session import Session
from flask_mail import Mail
from app.log.logger import setup_logger



app = Flask(__name__)
app.config.from_object(config['development'])
csrf = CSRFProtect(app)
lm = LoginManager()
mail = Mail(app)
setup_logger()
Session(app)
lm.login_view = 'index'
lm.refresh_view = 'index'
lm.login_message = u"Faça login para acessar!"
lm.needs_refresh_message = u"Sua sessão terminou, por favor faça login"
lm.needs_refresh_message_category = "info"
lm.init_app(app)


from app.model import forms, ModelUser
from app.controller import rotas

