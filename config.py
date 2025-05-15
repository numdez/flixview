from datetime import timedelta
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    SECRET_KEY=os.environ.get('SECRET_KEY')
    UPLOAD_FOLDER = '\\app\\uploads'
    SECRET_KEY='5643451654'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=120)
    SESSION_FILE_THRESHOLD = 200
    SESSION_TYPE = 'filesystem'
    MAIL_SERVER = 'email-ssl.com.br'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = ''
    MAIL_PASSWORD = f''
    MAIL_DEFAULT_SENDER = ''
    WTF_CSRF_TIME_LIMIT = 7200


config={
    'development':Config
}