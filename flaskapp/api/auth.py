import logging.config
from flask import Blueprint, jsonify, request, current_app

from extensions.token_utils import (refresh_token_required,
                                    generate_access_token,
                                    generate_refresh_token,
                                    decode_refresh_token)
from extensions.db import get_conn

blueprint = Blueprint(
    'auth',
    __name__,
    url_prefix='/api/v1')


@blueprint.route("/auth/get_access_token")
@refresh_token_required
def get_access_token():
    get_token = request.headers.get('Authorization')
    token = get_token.split()[-1]
    decoded = decode_refresh_token(token)
    decoded_json = decoded.json
    
    if decoded_json.get('ACK') == False: 
        current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {decoded_json.get('message')}")
        return jsonify({
            'ACK': False,
            'message':message
        })
    
    payload = decoded_json.get('payload')

    return jsonify({
        'ACK': True,
        'token': generate_access_token(payload.get('user_id'))
    })


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
                'password': u.get('password')
            } for u in db.users.find({'username': username})
        ]

    # validar dados

        credentialIsValid = username == user[0].get('username') and password == user[0].get('password')
                
    except IndexError:
        current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: Usuário ou senha inválidos")
        return jsonify({
            'ACK': False,
            'message': 'Usuário ou senha inválidos'
        })
    
    if credentialIsValid:
        current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: {username} realizou login com sucesso")
        return jsonify({
            'ACK': True,
            'token': generate_refresh_token(username)
            #'token': f'token-usuario {username}'
        })
        
    current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: Usuário ou senha inválidos")
    return jsonify({
            'ACK': False,
            'message': 'Usuário ou senha inválidos'
        })
