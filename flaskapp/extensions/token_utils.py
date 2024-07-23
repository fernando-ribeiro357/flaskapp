import datetime, logging.config
from os import getenv
from functools import wraps
from .db import get_conn

from flask import jsonify, request, current_app

import jwt

def sysadmin_required(fn):
    @wraps(fn)
    def sysadmin_required_wrap(*args, **kwargs):

        get_token = request.headers.get('Authorization')
        token = get_token.split()[-1]
        decoded = decode_access_token(token)
        decoded_json = decoded.json

        if decoded_json.get('ACK') == False:
            message = decoded_json.get('message')
            current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {decoded_json.get('message')}")
            return jsonify({
                'ACK': False,
                'message':message
            })
    
        payload = decoded_json.get('payload')

        user_id = payload.get('user_id')
        if user_id == None:
            message = 'user_id "None": Usuário(a) não logado'
            current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            return jsonify({
                'ACK': False,
                'message':message
            })
        try:

            # busca usuario no banco e verifica se possui perfil "sysadmin"
            db = get_conn('pessoa')
            count_users = db.users.count_documents({'username': user_id})
            if count_users == 0:
                message = f'user_id: {user_id} Usuário(a) não encontrado'
                current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
                return jsonify({
                    'ACK': False,
                    'message':message
                })
            
            user = db.users.find_one({'username': user_id})
            if user['profile'] != 'sysadmin':
                message = f"O(A) usuário(a) '{user['name']}' não possui perfil de sysadmin. (profile: {user['profile']})"
                current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
                return jsonify({
                    'ACK': False,
                    'message':message
                })
       
        except Exception as e:
            message = f"erro sysadmin_required: {e}"
            current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            return jsonify({
                'ACK': False,
                'message':message
            })

        return fn(*args,**kwargs)
    return sysadmin_required_wrap

def jwt_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
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
            jwt.decode(
                token,
                getenv('JWT_SECRET'),
                algorithms = ['HS256']
            )
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
        return fn(*args,**kwargs)
    return wrapped

def refresh_token_required(fn):
    @wraps(fn)
    def decoreted_function(*args, **kwargs):
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
            jwt.decode(
                token,
                getenv('JWT_REFRESH_SECRET'),
                algorithms = ['HS256']
            )
        except jwt.exceptions.ExpiredSignatureError:
            message = 'Token expirado'
            current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            return jsonify({
                'ACK': False,
                'message':message
            })

        except Exception as e:
            message = f'erro refresh_token_required: {e}'
            current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")            
            return jsonify({
                'ACK': False,
                'message':message
            })
        return fn(*args,**kwargs)
    return decoreted_function

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

def decode_refresh_token(refresh_token):
    try:
        payload = jwt.decode(refresh_token, getenv('JWT_REFRESH_SECRET'), algorithms=["HS256"])
        
    except jwt.exceptions.DecodeError:
        message = "Erro ao decodificar o refresh token"
        current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message':message
        })

    except Exception as e:
        message = f'erro decode_refresh_token: {e}'
        current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message':message
        })
    
    return jsonify({
            'ACK': True,
            'payload': payload
        })

def decode_access_token(access_token):
    try:
        payload = jwt.decode(access_token, getenv('JWT_SECRET'), algorithms=["HS256"])
        
    except jwt.exceptions.DecodeError:
        message = "Erro ao decodificar o refresh token"
        current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message':message
        })

    except Exception as e:
        message = f'erro decode_refresh_token: {e}'
        current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message':message
        })
    
    return jsonify({
            'ACK': True,
            'payload': payload
        })