from app.model.ModelUser import ModelUser
from app.controller.auth import Auth
from app.utils import utiles
from app.model import functions
from app.model.forms import LoginForm, AddAtendimentoForm, UpdateAtendimentoForm, AddMeusDadosForm, UpdateMeusDadosForm, AddUsuarioForm, UpdateUsuarioForm
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

@app.route('/meusdados', methods=["GET", "POST"])
@login_required
def base_dados():
    dados = functions.get_dados(current_user.id)
    if dados:
        return redirect(url_for('view_dados'))
    else:
        return redirect(url_for('add_dados'))

@app.route('/meusdados/add', methods=["GET", "POST"])
def add_dados():
    dados = utiles.to_df(functions.get_dados(current_user.id), 'dados')
    form = AddMeusDadosForm()
    if form.validate_on_submit():
        proc = f"""INSERT INTO tbl_undb_responsavel(id_responsavel, rua, num,
            complemento, bairro, cep, tel_fixo, tel_celular, email
        ) VALUES '{current_user.id}', '{form.rua.data}', '{form.num.data}', '{form.complemento.data}', 
        '{form.bairro.data}', '{form.cep.data}', '{form.tel_fixo.data}', '{form.tel_celular.data}', '{form.email.data}'
        """            
        functions.run_blank_set(proc)
        return redirect(url_for('base_dados'))
    return render_template('dados/add_dados.html', dados=dados)

@app.route('/meusdados/view', methods=["GET", "POST"])
def view_dados():
    dados = utiles.to_df(functions.get_dados(current_user.id), 'dados')
    return render_template('dados/view_dados.html', dados=dados)

@app.route('/meusdados/edit', methods=["GET", "POST"])
def edit_dados():
    form = UpdateMeusDadosForm()
    dados = utiles.to_df(functions.get_dados(current_user.id), 'dados')
    if form.validate_on_submit():
        rua = form.logradouro.data if form.logradouro.data != dados['rua'][0] else dados['rua'][0]
        num = form.num.data if form.num.data != dados['num'][0] else dados['unm'][0]
        complemento = form.cep.data if form.cep.data != dados['cep'][0] else dados['cep'][0]
        bairro = form.cep.data if form.cep.data != dados['cep'][0] else dados['cep'][0]
        cep = form.cep.data if form.cep.data != dados['cep'][0] else dados['cep'][0]
        tel_fixo = form.cep.data if form.cep.data != dados['cep'][0] else dados['cep'][0]
        tel_celular = form.cep.data if form.cep.data != dados['cep'][0] else dados['cep'][0]
        email = form.cep.data if form.cep.data != dados['cep'][0] else dados['cep'][0]
        proc = f"""
            UPDATE tbl_undb_responsaveis SET
            rua = '{rua}', num = '{num}', complemento = '{complemento}', bairro = '{bairro}',
            cep = '{cep}', tel_fixo = '{tel_fixo}', tel_celular = '{tel_celular}', email = '{email}'
            WHERE id_responsavel = {current_user.id}
        """
        functions.run_blank_set(proc)
        return redirect(url_for('base_dados'))
        #terminar / concluir
    return render_template('dados/edit_dados.html', dados=dados, form=form)

@app.route('/chamado/add', methods=['GET', 'POST'])
def add_chamado():
    form = AddAtendimentoForm()
    ids = []
    busca = DataFrame(functions.get_all_responsaveis(), 
                         columns=['id_usuario', 'nome_usuario'])
    for index, row in busca.iterrows():
        adicionar = str(row['id_usuario']) + ' - ' + str(row['nome_usuario'])
        ids.append(adicionar)  
    session['options'] = ids
    if form.validate_on_submit():
        if current_user.tipo != 'Usuário':
            form.id_usuario.data = form.nome_responsavel.data.split(' - ', 1)[0]
            form.nome_responsavel.data = form.nome_responsavel.data.split(' - ', 1)[1] 
        assinatura_base64 = request.form['assinaturaCanvasData']
        if assinatura_base64:
            assinatura_base64 = assinatura_base64.split(",")[1]
            assinatura_bytes = base64.b64decode(assinatura_base64)
            assinatura_io = BytesIO(assinatura_bytes)
            assinatura_string = base64.b64encode(assinatura_io.getvalue()).decode('utf-8')
        else:
            assinatura_string = ''
        if assinatura_string:
            if current_user.tipo == 'Usuário':
                proc = f"""INSERT INTO tbl_undb_chamados(id_usuario, 
                    data_atendimento, nome_aluno, data_nasc_aluno, serie_aluno, turma_aluno, nome_responsavel, 
                    parentesco_responsavel, email_responsavel, telefone_responsavel, celular_responsavel,
                    solicitado_por, questoes, aconselhamento, providencias, observacoes_finais, assinatura_responsavel
                ) VALUES """
                args = (current_user.id, datetime.today().date(), form.nome_aluno.data, form.nascimento_aluno.data,
                        form.serie_aluno.data, form.turma_aluno.data, form.nome_responsavel.data,
                        form.parentesco_responsavel.data, form.email_responsavel.data, 
                        form.telefone_responsavel.data, form.celular_responsavel.data, form.solicitado_por.data,
                        form.questoes.data, form.aconselhamento.data, form.providencias.data, 
                        form.observacoes_finais.data, assinatura_string
                    )
            elif current_user.tipo == 'Administrador' or current_user.tipo == 'Atendente':
                proc = f"""INSERT INTO tbl_undb_chamados(id_responsavel, id_usuario,
                    data_atendimento, nome_aluno, data_nasc_aluno, serie_aluno, turma_aluno, nome_responsavel, 
                    parentesco_responsavel, email_responsavel, telefone_responsavel, celular_responsavel,
                    solicitado_por, questoes, aconselhamento, providencias, observacoes_finais, assinatura_atendente
                ) VALUES """
                args = (current_user.id, form.id_usuario.data, datetime.today().date(), form.nome_aluno.data, form.nascimento_aluno.data,
                        form.serie_aluno.data, form.turma_aluno.data, form.nome_responsavel.data,
                        form.parentesco_responsavel.data, form.email_responsavel.data, 
                        form.telefone_responsavel.data, form.celular_responsavel.data, form.solicitado_por.data,
                        form.questoes.data, form.aconselhamento.data, form.providencias.data, 
                        form.observacoes_finais.data, assinatura_string
                    )
        else:
            if current_user.tipo == 'Usuário':
                proc = f"""INSERT INTO tbl_undb_chamados(id_usuario, 
                    data_atendimento, nome_aluno, data_nasc_aluno, serie_aluno, turma_aluno, nome_responsavel, 
                    parentesco_responsavel, email_responsavel, telefone_responsavel, celular_responsavel,
                    solicitado_por, questoes, aconselhamento, providencias, observacoes_finais
                ) VALUES """
                args = (current_user.id, datetime.today().date(), form.nome_aluno.data, form.nascimento_aluno.data,
                    form.serie_aluno.data, form.turma_aluno.data, form.nome_responsavel.data,
                    form.parentesco_responsavel.data, form.email_responsavel.data, 
                    form.telefone_responsavel.data, form.celular_responsavel.data, form.solicitado_por.data,
                    form.questoes.data, form.aconselhamento.data, form.providencias.data, 
                    form.observacoes_finais.data
                )
            elif current_user.tipo == 'Administrador' or current_user.tipo == 'Atendente':
                proc = f"""INSERT INTO tbl_undb_chamados(id_responsavel, id_usuario,
                    data_atendimento, nome_aluno, data_nasc_aluno, serie_aluno, turma_aluno, nome_responsavel, 
                    parentesco_responsavel, email_responsavel, telefone_responsavel, celular_responsavel,
                    solicitado_por, questoes, aconselhamento, providencias, observacoes_finais
                ) VALUES """
                args = (current_user.id, form.id_usuario.data, datetime.today().date(), form.nome_aluno.data, form.nascimento_aluno.data,
                    form.serie_aluno.data, form.turma_aluno.data, form.nome_responsavel.data,
                    form.parentesco_responsavel.data, form.email_responsavel.data, 
                    form.telefone_responsavel.data, form.celular_responsavel.data, form.solicitado_por.data,
                    form.questoes.data, form.aconselhamento.data, form.providencias.data, 
                    form.observacoes_finais.data
                )
            
        id = functions.run_blank_query(proc, args)
        return redirect(url_for('home'))
        #return redirect(url_for('view_atendimento', id_atendimento=id))
    return render_template('chamados/add_chamado.html', form=form, options=ids)

@app.route('/chamado/view/<id_chamado>', methods=["GET", "POST"])
def view_chamado(id_chamado):
    chamado = utiles.to_df(functions.get_chamado(id_chamado), 'chamado')
    chamado = utiles.limpaDatas(chamado)
    log_action(current_user.nome, 'VIEW', 'CHAMADO', id_chamado)
    if isinstance(chamado['assinatura_responsavel'][0], str):
        ass_responsavel = utiles.b64_to_bytes(chamado['assinatura_responsavel'][0])
        ass_responsavel = base64.b64encode(ass_responsavel).decode('utf-8')
    else:
        ass_responsavel = ''
    if isinstance(chamado['assinatura_atendente'][0], str):
        ass_atendente = utiles.b64_to_bytes(chamado['assinatura_atendente'][0])
        ass_atendente = base64.b64encode(ass_atendente).decode('utf-8')
    else:
        ass_atendente = ''
    return render_template('chamados/view_chamado.html', chamado=chamado, ass_responsavel=ass_responsavel, ass_atendente=ass_atendente)

@app.route('/view/chamados', methods=["GET", "POST"])
def all_chamados():
    current_user.mostra_valores()
    if current_user.tipo == 'Usuário':
        chamados = utiles.to_df(functions.get_chamados_usuario(session["_user_id"]), 'chamado')
    if current_user.tipo == 'Administrador' or current_user.tipo == 'Atendente':
        chamados = utiles.to_df(functions.get_chamados_responsavel(session["_user_id"]), 'chamado')
    chamados = utiles.limpaDatas(chamados)
    return render_template('atendimentos.html', df_atendimentos=chamados)

@app.route('/chamado/edit/<id_chamado>', methods=["GET", "POST"])
def edit_chamado(id_chamado):
    chamado = utiles.to_df(functions.get_chamado(id_chamado), 'chamado')
    form = UpdateAtendimentoForm()
    log_action(current_user.nome, 'EDIT', 'CHAMADO', id_chamado)
    
    if request.method == 'GET':
        if isinstance(chamado['assinatura_responsavel'][0], str):
            ass_responsavel = utiles.b64_to_bytes(chamado['assinatura_responsavel'][0])
            ass_responsavel = base64.b64encode(ass_responsavel).decode('utf-8')
        else:
            ass_responsavel = ''
        if isinstance(chamado['assinatura_atendente'][0], str):
            ass_atendente = utiles.b64_to_bytes(chamado['assinatura_atendente'][0])
            ass_atendente = base64.b64encode(ass_atendente).decode('utf-8')
        else:
            ass_atendente = ''
        form.questoes.data = chamado['questoes'][0]
        form.aconselhamento.data = chamado['aconselhamento'][0]
        form.providencias.data = chamado['providencias'][0]
        form.observacoes_finais.data = chamado['observacoes_finais'][0]
        ass_responsavel = chamado['assinatura_responsavel'][0] if chamado['assinatura_responsavel'][0] else 'Sem Assinatura'
        ass_atendente = chamado['assinatura_atendente'][0] if chamado['assinatura_atendente'][0] else 'Sem Assinatura'

    if form.validate_on_submit():
        assinatura_base64 = request.form['assinaturaCanvasData']
        if assinatura_base64:
            assinatura_base64 = assinatura_base64.split(",")[1]
            assinatura_bytes = base64.b64decode(assinatura_base64)
            assinatura_io = BytesIO(assinatura_bytes)
            assinatura_string = base64.b64encode(assinatura_io.getvalue()).decode('utf-8')
        else:
            assinatura_string = ''

        nome_aluno = form.nome_aluno.data if form.nome_aluno.data != chamado['nome_aluno'][0] else chamado['nome_aluno'][0]
        nascimento_aluno = form.nascimento_aluno.data if form.nascimento_aluno.data != chamado['data_nasc_aluno'][0] else chamado['data_nasc_aluno'][0]
        serie_aluno = form.serie_aluno.data if form.serie_aluno.data != chamado['serie_aluno'][0] else chamado['serie_aluno'][0]
        turma_aluno = form.turma_aluno.data if form.turma_aluno.data != chamado['turma_aluno'][0] else chamado['turma_aluno'][0]
        nome_responsavel = form.nome_responsavel.data if form.nome_responsavel.data != chamado['nome_responsavel'][0] else chamado['nome_responsavel'][0]
        parentesco_responsavel = form.parentesco_responsavel.data if form.parentesco_responsavel.data != chamado['parentesco_responsavel'][0] else chamado['parentesco_responsavel'][0]
        email_responsavel = form.email_responsavel.data if form.email_responsavel.data != chamado['email_responsavel'][0] else chamado['email_responsavel'][0]
        telefone_responsavel = form.telefone_responsavel.data if form.telefone_responsavel.data != chamado['telefone_responsavel'][0] else chamado['telefone_responsavel'][0]
        celular_responsavel = form.celular_responsavel.data if form.celular_responsavel.data != chamado['celular_responsavel'][0] else chamado['celular_responsavel'][0]
        solicitado_por = form.solicitado_por.data if form.solicitado_por.data != chamado['solicitado_por'][0] else chamado['solicitado_por'][0]
        questoes = form.questoes.data if form.questoes.data != chamado['questoes'][0] else chamado['questoes'][0]
        aconselhamento = form.aconselhamento.data if form.aconselhamento.data != chamado['aconselhamento'][0] else chamado['aconselhamento'][0]
        providencias = form.providencias.data if form.providencias.data != chamado['providencias'][0] else chamado['providencias'][0]
        observacoes_finais = form.observacoes_finais.data if form.observacoes_finais.data != chamado['observacoes_finais'][0] else chamado['observacoes_finais'][0]
        if assinatura_string:
            if current_user.tipo == 'Usuário':
                ass_responsavel = assinatura_string
                ass_atendente = '' if not chamado['assinatura_atendente'][0] else chamado['assinatura_atendente'][0]
            else:
                ass_responsavel = '' if not chamado['assinatura_responsavel'][0] else chamado['assinatura_responsavel'][0]
                ass_atendente = assinatura_string
            proc = f"""
                UPDATE tbl_undb_chamados SET nome_aluno = '{nome_aluno}', data_nasc_aluno = '{nascimento_aluno}', 
                serie_aluno = '{serie_aluno}', turma_aluno = '{turma_aluno}', nome_responsavel = '{nome_responsavel}',
                parentesco_responsavel = '{parentesco_responsavel}', email_responsavel = '{email_responsavel}',
                telefone_responsavel = '{telefone_responsavel}', celular_responsavel = '{celular_responsavel}',
                solicitado_por = '{solicitado_por}', questoes = '{questoes}', aconselhamento = '{aconselhamento}',
                providencias = '{providencias}', observacoes_finais = '{observacoes_finais}', 
                assinatura_responsavel = '{ass_responsavel}', assinatura_atendente = '{ass_atendente}'
                where id_chamado = {id_chamado}
            """
            functions.run_blank_set(proc)

            return redirect(url_for('view_chamado', id_chamado=id_chamado))
    if isinstance(chamado['assinatura_responsavel'][0], str):
        ass_responsavel = utiles.b64_to_bytes(chamado['assinatura_responsavel'][0])
        ass_responsavel = base64.b64encode(ass_responsavel).decode('utf-8')
    else:
        ass_responsavel = ''
    if isinstance(chamado['assinatura_atendente'][0], str):
        ass_atendente = utiles.b64_to_bytes(chamado['assinatura_atendente'][0])
        ass_atendente = base64.b64encode(ass_atendente).decode('utf-8')
    else:
        ass_atendente = ''
    return render_template('/chamados/edit_chamado.html', chamado=chamado, form=form, ass_responsavel=ass_responsavel, ass_atendente=ass_atendente)

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
            INSERT INTO tbl_undb_usuarios (nome_usuario, email_usuario, senha_usuario, tipo_usuario)
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