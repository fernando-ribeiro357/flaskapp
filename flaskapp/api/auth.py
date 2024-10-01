from os import getenv
import logging.config
from passlib.hash import pbkdf2_sha256
from flask import (Blueprint, 
                   jsonify,
                   json,
                   request, 
                   current_app,
                   flash,
                   redirect,
                   make_response)

from extensions.token_utils import (generate_token,
                                    decode_token)
from extensions.db import get_conn

blueprint = Blueprint(
    'auth',
    __name__,
    url_prefix='/api/v1')


@blueprint.route("/auth", methods = ['POST'])
def auth():
    # {username: usuario, password: senha}
    username = request.json.get('username')
    password = request.json.get('password')
    ## fazer consulta no banco
    db = get_conn('pessoa')
    
    try:
        user = [
            {
                'username': u.get('username'),
                'name': u.get('name'),
                'password': u.get('password'),
                'profile': u.get('profile')
            } for u in db.users.find({'username': username,'deleted_at': None})
        ]

        # validar dados
        credentialIsValid = pbkdf2_sha256.verify(password, user[0].get('password'))

    except IndexError:
        message = "Usuário ou senha inválidos"
        current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message': message
        })
    
    if credentialIsValid:
        message = f"{user[0].get('name')} realizou login com sucesso"
        current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        token = generate_token(username)
        response = make_response(jsonify({
                'ACK': True,
                'user_name': user[0].get('name'),
                'token': token
            }))
        return response
        
        
    current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: Usuário ou senha inválidos")
    return jsonify({
            'ACK': False,
            'message': 'Usuário ou senha inválidos'
        })

def is_logged():
    if 'token' in request.cookies and 'user_id' in request.cookies:
        return True

    return False

def hash_password(plain):
    return pbkdf2_sha256.hash(plain)
    
