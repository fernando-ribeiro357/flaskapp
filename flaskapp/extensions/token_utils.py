import datetime, logging.config
from os import getenv
from functools import wraps
from .db import get_conn

from flask import jsonify, request, current_app

import jwt

def access_token_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        retorno = jwt_required(getenv('JWT_SECRET'))
        jsonData = retorno.json
    
        if jsonData.get('ACK') == False:
            return jsonData

        return fn(*args,**kwargs)
    return wrapped

def refresh_token_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        retorno = jwt_required(getenv('JWT_REFRESH_SECRET'))
        jsonData = retorno.json
    
        if jsonData.get('ACK') == False:
            return jsonData

        return fn(*args,**kwargs)
    return wrapped

def jwt_required(jwt_secret):    
    get_token = request.headers.get('Authorization')
    if (get_token == None):
        message = 'Token Nulo'
        current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message':message
        })
    
    token = get_token.split()[-1]
    try:
        
        payload = jwt.decode(token, jwt_secret, algorithms = ['HS256'])

    except jwt.exceptions.ExpiredSignatureError:
        message = 'Token expirado'
        current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message':message
        })
    except jwt.exceptions.InvalidSignatureError:
        message = 'Token inválido'
        current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message':message
        })
    except jwt.exceptions.DecodeError:
        message = 'Token inválido'
        current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message':message
        })
    except Exception as e:
        message = f'erro jwt_required: {e}'
        current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message':message
        })
        
    return jsonify({
        'ACK': True,
        'message': 'Token ok.',
        'data': payload
    })
    


def generate_access_token(user_id):
    try:
        token_acesso = jwt.encode(
            {
                'user_id': user_id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
            },
            getenv('JWT_SECRET'),
            algorithm='HS256'
        )
        current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: token de acesso gerado para {user_id}")
        return token_acesso
    except Exception as e:
        message = f'erro generate_access_token: {e}'
        current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message':message
        })

def generate_refresh_token(user_id):
    try:
        token_refresh = jwt.encode(
            {
                'user_id': user_id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=3000)
            },
            getenv('JWT_REFRESH_SECRET'),
            algorithm='HS256'
        )
        current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: token de acesso gerado para {user_id}")
        return token_refresh
    except Exception as e:
        message = f'erro generate_refresh_token: {e}'
        current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message':message
        })

def decode_token(token, secret):    
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        
    except jwt.exceptions.DecodeError:
        message = "Erro ao decodificar o token"
        current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message':message
        })

    except Exception as e:
        message = f'erro decode_token: {e}'
        current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message':message
        })
    
    return jsonify({
            'ACK': True,
            'payload': payload
        })
