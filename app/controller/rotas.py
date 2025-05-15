from app.model.ModelUser import ModelUser
from app.controller.auth import Auth
from app.utils import utiles
from app.model import functions
from app.model.forms import LoginForm, AddUsuarioForm, UpdateUsuarioForm
from app.model.entidades.Usuario import Usuario
from app.log.logger import log_action

import base64
from io import BytesIO
from PIL import Image

import requests
import os
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from flask_login import logout_user, login_user, login_required, current_user
from flask import render_template, flash, redirect, url_for, request, abort, session, jsonify, send_file, make_response
from werkzeug.utils import secure_filename
from datetime import timedelta, datetime
from pandas import DataFrame
from app import app, lm




# Login_manager
@lm.user_loader
def load_user(id):
    db_loader = ModelUser()
    lm.session_protection = "strong"
    data = ModelUser.get_by_id(db_loader, id)
    return data


# ROUTE
# Login
@app.route("/", methods=["GET", "POST"])
def index():
    db = ModelUser()
    form = LoginForm()
    next_url = form.next.data 
    if current_user.is_authenticated:
        if next_url:
            return redirect(next_url)
        session['ultAbaAberta'] = 'home'
        return redirect(url_for('home'))
    if form.validate_on_submit():
        user = Usuario(0, form.email.data, form.senha.data)
        logged_user = ModelUser.login(db, user)
        if isinstance(logged_user, str):
            logged_user = None
        if logged_user and logged_user.senha:
            login_user(logged_user, remember=False)
            log_action(logged_user.nome, 'LOGIN')
            return redirect(next_url or url_for('home'))
        flash("Usuário ou senha incorretos.")
    else:
        print(form.errors)
    return render_template('login.html', form=form)

# Login com OAuth
@app.route("/auth/login", methods=["GET", "POST"])
def auth_login():
    client_id = os.getenv('CLIENT_ID')
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri=http://127.0.0.1:5000/auth&response_type=code&scope=email")

# Callback de autenticação Google
@app.route("/auth", methods=["GET", "POST"])
def auth():
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    code = request.args.get('code')

    token_url = 'https://oauth2.googleapis.com/token'
    payload = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': 'http://127.0.0.1:5000/auth',
        'grant_type': 'authorization_code'
    }
    response = requests.post(token_url, data=payload)
    response_data = response.json()

    if 'error' in response_data:
        flash("Erro ao buscar usuário")
        return redirect(url_for('index'))

    access_token = response_data.get('access_token')

    user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo?access_token=" + access_token
    user_info_response = requests.get(user_info_url)

    if user_info_response.status_code != 200:
        print(user_info_response.json())
        flash("Erro ao buscar usuário")
        return redirect(url_for('index'))
    
    user_info = user_info_response.json()
    email = user_info['email']

    db = ModelUser()
    user = ModelUser.auth_login(db, email)
    
    if user:
        login_user(user, remember=False)
        return redirect(url_for('home'))
    else:
        flash("Usuário não cadastrado")
        return redirect(url_for('index'))


# Logout
@app.route("/logout")
@login_required
def logout():
    user = functions.get_usuario(current_user.id)
    logout_user()
    log_action(user[0][1], 'LOGOUT')
    session.clear()
    resp = make_response(redirect(url_for("index")))
    return resp


@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    id_user = session["_user_id"]
    current_user.atualiza_login()
    functions.loga_usuario(id_user)
    session['ultAbaAberta'] = 'home'
    usuario = utiles.to_df(functions.get_usuario(id_user), 'usuario')
    return render_template('base.html')

@app.route('/usuarios', methods=["GET", "POST"])
def all_usuarios():
    if current_user.tipo != 'Administrador':
        return redirect(url_for('home'))
    usuarios = utiles.to_df(functions.get_all_usuarios(), 'usuario')
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/usuarios/add', methods=["GET", "POST"])
def add_usuario():
    if current_user.tipo != 'Administrador':
        return redirect(url_for('home'))
    form = AddUsuarioForm()
    form.tipo_usuario.choices = ["", "Usuário", "Atendente", "Administrador"]
    if form.validate_on_submit():
        senha_usuario = Usuario.create_password(form.senha_usuario.data)
        proc = """
            INSERT INTO tbl_undb_usuarios (nome, email, senha, tipo)
            VALUES"""
        args = (form.nome_usuario.data, form.email_usuario.data, senha_usuario, form.tipo_usuario.data)
        functions.run_blank_query(proc, args)
        return redirect(url_for('all_usuarios'))
    # terminar / concluir
    return render_template('usuarios/add_usuario.html', form=form)

@app.route('/usuarios/view/<id_usuario>', methods=["GET", "POST"])
def view_usuario(id_usuario):
    usuario = utiles.to_df(functions.get_usuario(id_usuario), 'usuario')
    return render_template('usuarios/view_usuario.html', usuario=usuario)

# FUNCTIONS HTTP
def status_404(error):
    return "<h1>Pagina não encontrada</h1>", 404

def status_403(error):
    return "<h1>Sistema pausado</h1>", 403

def status_500(error):
    return "<h1>Sistema em Manutenção</h1>", 500

@app.errorhandler(500)
def erro_interno(error):
    print('deu erro interno:', error)
    #return redirect(url_for('home'))

@app.errorhandler(401)
def page_not_auto(error):
    return "<h3>Acesso não Autorizado!</h3>", 401