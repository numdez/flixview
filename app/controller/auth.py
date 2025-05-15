from pyotp import TOTP, random_base32
from flask import jsonify
from io import BytesIO
import qrcode
import base64

class Auth():

    def __init__(self):
        self._secret = self._get_secret()
        self._totp = self._get_secret()

    def _get_secret(self):
        data = random_base32()
        return data

    def _get_totp(self):
        data = TOTP(self._secret)
        return data
    
    @classmethod
    def get_totp_uri(self, name):
        data = self._totp.provisioning_uri(name=name, issuer_name='Atendimentos')
        return data
    
    @classmethod
    def get_totp_qrcode(self, name):
        img = qrcode.make(self.get_totp_uri(name))
        imgBytes = BytesIO()
        img.save(imgBytes)
        imgBytes.seek(0)
        imgUrl = base64.b64encode(imgBytes.getvalue()).decode()
        return jsonify({'qrcode': imgUrl})

    @classmethod
    def confirm_totp(self, digits):
        data = self._totp.verify(digits)
        return data
