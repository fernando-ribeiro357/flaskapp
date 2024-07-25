import logging.config
from flask import Blueprint, jsonify, request, current_app

from extensions.token_utils import (access_token_required, sysadmin_required, decode_access_token)
from extensions.db import get_conn

blueprint = Blueprint('profile',
                      __name__,
                      url_prefix='/api/v1')


@blueprint.route("/get_profiles")
@access_token_required
@sysadmin_required
def get_profiles():
    db = get_conn('pessoa')
    try:
        profiles_data = [
            {
                'name': u['name'],
                'username': u['username'],
                'profile': u['profile'],
                'email': u['email'],
                'created_at': u['created_at'],
                'updated_at': u['updated_at'],
                'deleted_at': u['deleted_at']
            } for u in db.users.find({'deleted_at': None})
        ]
    
    except Exception as e:
        message = f"erro get_profile_data: {e}"
        current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message': message
        })
    
    return jsonify({
        'ACK': True,
        'data': profiles_data
    })

@blueprint.route("/get_profile_data")
@access_token_required
def get_profile_data():
    # # Busca o user_id no access_token
    # get_token = request.headers.get('Authorization')
    # token = get_token.split()[-1]
    # decoded = decode_access_token(token)
    # decoded_json = decoded.json
    
    # if decoded_json.get('ACK') == False: 
    #     current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {decoded_json.get('message')}")
    #     return jsonify({
    #         'ACK': False,
    #         'message':message
    #     })
    # payload = decoded_json.get('payload')
    # user_id = payload.get('user_id')

    user_id = request.cookies.get('user_id')
        
    try:
        db = get_conn('pessoa')
        profile_data = [
            {
                'name': u['name'],
                'username': u['username'],
                'profile': u['profile'],
                'email': u['email'],
                'created_at': u['created_at'],
                'updated_at': u['updated_at']
            } for u in db.users.find({'username':user_id})
        ]
    
    except Exception as e:
        message = f"erro get_profile_data: {e}"
        current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message': message
        })
        
    return jsonify({
        'ACK': True,
        'data': profile_data
    })


@blueprint.route("/update_profile", methods = ["PUT"])
@access_token_required
@sysadmin_required
def update_profile():
    db = get_conn('pessoa')

    user = dict(request.json)
    count_users = db.users.count_documents({'username': user.get('username')})
    
    if count_users != 1:
        message='Usuário não encontrado.'
        current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message': message
        }), 400

    db.users.update_one({'username': user.get('username')},{"$set": user})
    message=f"Perfil do usuário {user.get('username')} alterado com sucesso"
    current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: {message}")
    return jsonify({
        'ACK': True,
        'message': message,
        'usuário':dict(request.json)
    })


@blueprint.route("/insert_profile", methods = ["POST"])
@access_token_required
@sysadmin_required
def insert_profile():

    db = get_conn('pessoa')

    user = dict(request.json)
    count_users = db.users.count_documents({'username': user.get('username')})
    count_email = db.users.count_documents({'email': user.get('email')})
    if count_users > 0 or count_email > 0:
        message='O nome de login ou e-mail já foram utilizados'
        current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message': message
        }), 400

    db.users.insert_one(user)
    message='Usuário inserido com sucesso'
    current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: {message}")
    return jsonify({
        'ACK': True,
        'message': message,
        'usuário':dict(request.json)
    })
