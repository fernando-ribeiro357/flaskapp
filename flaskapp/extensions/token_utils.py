import datetime, logging.config
from os import getenv
from functools import wraps
from .db import get_conn

from flask import (jsonify, 
                   request, 
                   current_app, 
                   make_response, 
                   redirect,
                   flash)

import jwt

def token_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        get_token = request.cookies.get('token')

        if (get_token == None):
            message = 'Token nulo'
            current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            flash(message)
            retorno = make_response(redirect('/'))
            return retorno
        
        # token = get_token.split()[-1]
        token = get_token
        try:
            payload = jwt.decode(token, getenv('JWT_SECRET'), algorithms = ['HS256'])

        except jwt.exceptions.ExpiredSignatureError:
            message = 'Token expirado'
            current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            flash(message)
            retorno = make_response(redirect('/'))
            return retorno

        except jwt.exceptions.InvalidSignatureError:
            message = 'Token inválido'
            current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            flash(message)
            retorno = make_response(redirect('/'))
            return retorno

        except jwt.exceptions.DecodeError:
            message = 'Erro ao decodificar o token'
            current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            flash(message)
            return make_response(redirect('/'))

        except Exception as e:
            message = f'Erro token: {e}'
            current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            flash(message)
            return make_response(redirect('/'))
            
        message = 'Token OK.'
        current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: {message}")

        return fn(*args,**kwargs)
    return wrapped


def generate_token(user_id):
    try:
        token = jwt.encode(
            {
                'user_id': user_id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            },
            getenv('JWT_SECRET'),
            algorithm='HS256'
        )
        
    except Exception as e:
        message = f'Erro ao gerar o token: {e}'
        current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        flash(message)
        return make_response(redirect('/'))
    
    message = f"Token gerado para {user_id}"
    current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: {message}")
    return token
    


def decode_token(token):    
    try:
        payload = jwt.decode(token, getenv('JWT_SECRET'), algorithms=["HS256"])
        
    except jwt.exceptions.DecodeError:
        message = "Erro ao decodificar o token"
        current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message':message
        })

    except Exception as e:
        message = f'Erro ao decodificar o token: {e}'
        current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message':message
        })
    
    message = "payload extraído do token"
    current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: {message}")
    return jsonify({
        'ACK': True,
        'message':message,
        'payload': payload
    })
    