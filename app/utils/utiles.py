import pandas as pd
from io import BytesIO
from flask_login import current_user
from flask import redirect, url_for, abort, jsonify
from app.model import functions
from time import sleep
import base64

def to_df(data, tabela):
    if data:
        match tabela.lower():
            case 'usuario':
                data = pd.DataFrame(
                    data, 
                    columns=['id_usuario', 'nome_usuario', 'email_usuario', 'senha_usuario', 'ult_data_login', 'tipo_usuario', 'assinatura']
                )
            case 'chamado':
                data = pd.DataFrame(
                    data, 
                    columns=['id_chamado', 'id_responsavel', 'id_usuario', 'data_atendimento', 'nome_aluno', 'data_nasc_aluno',
                        'serie_aluno', 'turma_aluno', 'nome_responsavel', 'parentesco_responsavel',
                        'email_responsavel', 'telefone_responsavel', 'celular_responsavel', 'solicitado_por',
                        'questoes', 'aconselhamento', 'providencias', 'observacoes_finais', 
                        'assinatura_responsavel', 'assinatura_atendente']
                )
            case 'dados':
                data = pd.DataFrame(
                    data,
                    columns=['id_responsavel', 'rua', 'num', 'complemento', 'bairro', 'cep', 'tel_fixo', 'tel_celular', 'email']
                )
    else:
        match tabela.lower():
            case 'usuario':
                data = pd.DataFrame( 
                    columns=['id_usuario', 'nome_usuario', 'email_usuario', 'senha_usuario', 'ult_data_login', 'tipo_usuario', 'assinatura']
                )
            case 'chamado':
                data = pd.DataFrame(
                    columns=['id_chamado', 'id_responsavel', 'id_usuario', 'data_atendimento', 'nome_aluno', 'data_nasc_aluno',
                        'serie_aluno', 'turma_aluno', 'nome_responsavel', 'parentesco_responsavel',
                        'email_responsavel', 'telefone_responsavel', 'celular_responsavel', 'solicitado_por',
                        'questoes', 'aconselhamento', 'providencias', 'observacoes_finais', 
                        'assinatura_responsavel', 'assinatura_atendente']
                )
            case 'dados':
                data = pd.DataFrame(
                    columns=['id_responsavel', 'rua', 'num', 'complemento', 'bairro', 'cep', 'tel_fixo', 'tel_celular', 'email']
                )
    return data

def normalize_dates(df):
    for col in df.columns:
        if df[col].dtype == 'object': 
            df[col] = pd.to_datetime(df[col], format="%Y-%m-%d", errors='ignore')
    for col in df.columns:
        if df[col].dtype == 'datetime64[ns]':
            df[col] = df[col].dt.strftime('%d/%m/%Y')
    return df

# REMOVER DATAS VAZIAS
def limpaDatas(df):
    data = normalize_dates(df)
    return data

def bytes_to_img(b64String):
    imageBytes = base64.b64decode(b64String)
    image_stream = BytesIO(imageBytes)
    return image_stream

def b64_to_bytes(b64String):
    imageBytes = base64.b64decode(b64String)
    return imageBytes