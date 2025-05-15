from werkzeug.security import generate_password_hash, check_password_hash

senhaBruta = input('Insira a senha que deve ser criptografada: ')

senhaCripto = generate_password_hash(senhaBruta, salt_length=16)

print(f"'{senhaBruta}' virou '{senhaCripto}'")