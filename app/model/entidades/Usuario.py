from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class Usuario(UserMixin):
    def __init__(self,id,email,senha,nome="",tipo="", ult_data="") -> None:
        self.id = id
        self.email = email
        self.senha = senha
        self.nome = nome
        self.tipo = tipo
        self.ultimo_login = ult_data
        
    def mostra_valores(self):
        print(f'id: {self.id}')
        print(f'email: {self.email}')
        print(f'senha: {self.senha}')
        print(f'nome: {self.nome}')
        print(f'tipo: {self.tipo}')
        print(f'ultimo login: {self.ultimo_login}')

    def atualiza_login(self):
        self.ultimo_login = datetime.today().date()

    @classmethod
    def verify_password(self,hashed_password, senha):
        resultado = check_password_hash(hashed_password,senha)
        return resultado
    
    @classmethod
    def create_password(self, senha):
        senhaCripto = generate_password_hash(senha, salt_length=16)
        return senhaCripto