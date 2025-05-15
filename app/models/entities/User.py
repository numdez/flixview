from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self,id,email,pwd,name="",access="") -> None:
        self.id = id
        self.email = email
        self.pwd = pwd
        self.name = name
        self.access = access

    @classmethod
    def verify_pwd(self,hashed_password, pwd):
        return check_password_hash(hashed_password,pwd)
    
    #Adicionado na att 20/05/2024
    @classmethod
    def create_pwd(self, pwd):
        return generate_password_hash(pwd, salt_length=16)