import datetime, logging.config
from os import getenv
from functools import wraps

from flask import jsonify, redirect, request, current_app

import jwt

def jwt_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        token = request.headers.get('Authorization').split()[-1]

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
            message = f'erro: {e}'
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
        token = request.cookies.get('token')
        #{token: token-vem--aqui}

        try:
            jwt.decode(
                token,
                getenv('JWT_REFRESH_SECRET'),
                algorithms = ['HS256']
            )
        except jwt.exceptions.ExpiredSignatureError:
            message = 'Token expirado'
            current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            return redirect("/login")

        except Exception as e:
            message = f'erro: {e}'
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
        message = f'erro: {e}'
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
        message = f'erro: {e}'
        current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message':message
        })
    