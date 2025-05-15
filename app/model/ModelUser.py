from .entidades.Usuario import Usuario
import pandas as pd
import sqlite3


class ModelUser():
    def __init__(self):
        self._nome = 'app.db'
        self._conn = self._connecting()

    def _connecting(self):
        conn = sqlite3.connect(self._nome)
        return conn


    @classmethod
    def login(self, db, user):
        try:
            cursor = db._conn.cursor()
            sql = (
                f"SELECT * FROM tbl_undb_usuarios WHERE email_usuario = '{user.email}'")
            row = cursor.execute(sql).fetchone()
            if row != None:
                usuario = pd.DataFrame(
                    [row], 
                    columns=['id_usuario', 'nome_usuario', 'email_usuario', 'senha_usuario', 'ult_data_login', 'tipo_usuario', 'assinatura']
                )
                if Usuario.verify_password(usuario['senha_usuario'][0], user.senha):
                    usuario = Usuario(usuario['id_usuario'][0], usuario['email_usuario'][0], usuario['senha_usuario'][0], 
                            usuario['nome_usuario'][0], usuario['tipo_usuario'][0], usuario['ult_data_login'][0])
                else:
                    usuario = 'Senha ou email inválido(s)!'
                db._conn.close()
                return usuario
            else:
                return None
        except Exception as ex:
            raise Exception(ex)
    
    
    @classmethod
    def auth_login(self, db, email):
        try:
            cursor = db._conn.cursor()
            sql = (
                f"SELECT * FROM tbl_undb_usuarios WHERE email_usuario = '{email}'")
            row = cursor.execute(sql).fetchone()
            if row != None:
                user = pd.DataFrame(
                    [row], 
                    columns=['id_usuario', 'nome_usuario', 'email_usuario', 'senha_usuario', 'ult_data_login', 'tipo_usuario', 'assinatura']
                )
                user = Usuario(user['id_usuario'][0], user['email_usuario'][0], user['senha_usuario'][0], 
                            user['nome_usuario'][0], user['tipo_usuario'][0], user['ult_data_login'][0])
                db._conn.close()
                return user
            else:
                return None
        except Exception as ex:
            raise Exception(ex)
    


    @classmethod
    def get_by_id(self, db_loader, id):
        cursor = db_loader._conn.cursor()
        sql = (
            f'SELECT * FROM tbl_undb_usuarios WHERE id_usuario={id}'
        )
        
        row = cursor.execute(sql).fetchone()
        if row != None:
            logged_user = pd.DataFrame(
                    [row], 
                    columns=['id_usuario', 'nome_usuario', 'email_usuario', 'senha_usuario', 'ult_data_login', 'tipo_usuario', 'assinatura']
                )
            logged_user = Usuario(logged_user['id_usuario'][0], logged_user['email_usuario'][0], logged_user['senha_usuario'][0], 
                            logged_user['nome_usuario'][0], logged_user['tipo_usuario'][0], logged_user['ult_data_login'][0])
            return logged_user
        else:
            return None
        
    @classmethod
    def add(self, db, user):
        try:
            cursor = db._conn.cursor()
            sql = (
                f"INSERT INTO tbl_undb_usuarios (nome_usuario, email_usuario, senha_usuario, tipo_usuario, assinatura) "
                f"VALUES ('{user.nome}', '{user.email}', '{user.senha}', '{user.tipo}', '{user.assinatura}')"
            )
            cursor.execute(sql)
            db._conn.commit()
            db._conn.close()
            return "Usuário adicionado com sucesso!"
        except Exception as ex:
            raise Exception("Erro ao adicionar usuário: " + str(ex))

    @classmethod
    def get_all(self, db):
        try:
            cursor = db._conn.cursor()
            sql = "SELECT * FROM tbl_undb_usuarios"
            rows = cursor.execute(sql).fetchall()
            usuarios = pd.DataFrame(rows, columns=['id_usuario', 'nome_usuario', 'email_usuario', 'senha_usuario', 'ult_data_login', 'tipo_usuario', 'assinatura'])
            db._conn.close()
            return usuarios
        except Exception as ex:
            raise Exception("Erro ao listar usuários: " + str(ex))

    @classmethod
    def update(self, db, user):
        try:
            cursor = db._conn.cursor()
            sql = (
                f"UPDATE tbl_undb_usuarios SET "
                f"nome_usuario = '{user.nome}', "
                f"email_usuario = '{user.email}', "
                f"senha_usuario = '{user.senha}', "
                f"tipo_usuario = '{user.tipo}', "
                f"assinatura = '{user.assinatura}' "
                f"WHERE id_usuario = {user.id}"
            )
            cursor.execute(sql)
            db._conn.commit()
            db._conn.close()
            return "Usuário atualizado com sucesso!"
        except Exception as ex:
            raise Exception("Erro ao atualizar usuário: " + str(ex))

    @classmethod
    def delete(self, db, id):
        try:
            cursor = db._conn.cursor()
            sql = f"DELETE FROM tbl_undb_usuarios WHERE id_usuario = {id}"
            cursor.execute(sql)
            db._conn.commit()
            db._conn.close()
            return "Usuário excluído com sucesso!"
        except Exception as ex:
            raise Exception("Erro ao excluir usuário: " + str(ex))

    @classmethod
    def call_get_query(self, db, query):
        temp = []
        results = []
        try:
            cursor = db._conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                temp = [elem for elem in row]
                results.append(temp)
            db._conn.close()
            if results:
                return results
            else:
                return ''
        except Exception as ex:
            raise Exception(ex)
    

    @classmethod
    def call_set_query(self, db, query):
        try:
            cursor = db._conn.cursor()
            cursor.execute(query)
            db._conn.commit()
            db._conn.close()
        except Exception as ex:
            raise Exception(ex)
        
    
    @classmethod
    def call_bimethod_query(self, db, query):
        cursor = db._conn.cursor()
        cursor.execute(query)
        results = cursor.fetchone()[0]
        cursor.commit()
        db._conn.close()
        return results