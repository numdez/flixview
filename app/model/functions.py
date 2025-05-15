from app.model.ModelUser import ModelUser
from datetime import datetime

def get_all_chamados():
    db = ModelUser()
    proc = "SELECT * FROM tbl_undb_chamados"
    data = ModelUser.call_get_query(db, proc)
    return data

def get_all_usuarios():
    db = ModelUser()
    proc = "SELECT * FROM tbl_undb_usuarios"
    data = ModelUser.call_get_query(db, proc)
    return data

def get_usuario(id):
    db = ModelUser()
    proc = f"SELECT * FROM tbl_undb_usuarios WHERE id_usuario = {id}"
    data = ModelUser.call_get_query(db, proc)
    return data

def loga_usuario(id):
    db = ModelUser()
    dataAtual = datetime.today().date()
    proc = f"UPDATE tbl_undb_usuarios SET ult_data_login = '{dataAtual}' WHERE id_usuario = {id}"
    ModelUser.call_set_query(db, proc)

def get_chamado(id):
    db = ModelUser()
    proc = f"SELECT * FROM tbl_undb_chamados WHERE id_chamado = {id}"
    data = ModelUser.call_get_query(db, proc)
    return data

def get_chamados_usuario(id):
    db = ModelUser()
    proc = f"SELECT * FROM tbl_undb_chamados WHERE id_usuario = {id}"
    data = ModelUser.call_get_query(db, proc)
    return data

def get_chamados_responsavel(id):
    db = ModelUser()
    proc = f"SELECT * FROM tbl_undb_chamados WHERE id_responsavel = {id} or id_responsavel is null"
    data = ModelUser.call_get_query(db, proc)
    return data

def get_all_responsaveis():
    db = ModelUser()
    proc = "SELECT id_usuario, nome_usuario FROM tbl_undb_usuarios WHERE tipo_usuario = 'Usuário'"
    data = ModelUser.call_get_query(db, proc)
    return data

def get_dados(id):
    db = ModelUser()
    proc = f"SELECT * FROM tbl_undb_responsavel WHERE id_responsavel = {id}"
    data = ModelUser.call_get_query(db, proc)
    return data

def run_blank_query(proc, args):
    db = ModelUser()
    proc += '('
    proc += f'"{args[0]}"'
    for i in args[1:]:
        proc += f',"{i}"' 
    proc += ')'
    data = ModelUser.call_set_query(db, proc)
    return data

def run_blank_get(proc):
    db = ModelUser()
    data = ModelUser.call_get_query(db, proc)
    return data

def run_blank_set(proc):
    db = ModelUser()
    ModelUser.call_set_query(db, proc)
