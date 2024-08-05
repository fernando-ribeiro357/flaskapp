import logging.config
from os import getenv
import json

from datetime import datetime

from flask_cors import cross_origin

from flask import Blueprint, jsonify, request, current_app

from extensions.token_utils import (access_token_required, decode_token)
from extensions.access_control import (sysadmin_required, sysadmin_owner_required, user_has_profile)
from extensions.db import get_conn

blueprint = Blueprint('profile',
                      __name__,
                      url_prefix='/api/v1')


@blueprint.route("/get_profiles")
@cross_origin()
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
        'message': 'Perfis buscados com sucesso',
        'data': profiles_data
    })

@blueprint.route("/get_profile_data")
@cross_origin()
@access_token_required
def get_profile_data():

    # user_id = request.cookies.get('user_id')

    get_token = request.headers.get('Authorization')
    if (get_token == None):
        message = 'Token Nulo'
        current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message':message
        })
    
    token = get_token.split()[-1]

    secret = getenv('JWT_SECRET')
        
    get_payload = decode_token(token, secret)

    payloadData = dict(get_payload.json)

    if payloadData.get('ACK') == False:
        return jsonify(payloadData)
    
    payload = payloadData.get('payload')
    user_id = payload.get('user_id')

    if user_id == None:
        message = f"erro user_id: {user_id}. Realize login novamente."
        current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message': message
        })
        
    try:
        db = get_conn('pessoa')
        user_profile = db.users.find_one({'username':user_id})
        profile_data = json.loads(json.dumps(user_profile, default=lambda x: list(x) if isinstance(x, tuple) else str(x)))
    
        return jsonify({
            'ACK': True,
            'message': 'Perfil buscado com sucesso',
            'data': [profile_data]
        })

    except Exception as e:
        message = f"erro get_profile_data: {e}"
        current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message': message
        })
        
    return jsonify({
        'ACK': True,
        'message': 'Perfil buscado com sucesso',
        'data': [profile_data]
    })


@blueprint.route("/update_profile", methods = ["PATCH"])
@cross_origin()
@access_token_required
@sysadmin_owner_required
def update_profile():
    user_id = request.cookies.get('user_id')
    try:        
        db = get_conn('pessoa')
        user = dict(request.json)
        count_users = db.users.count_documents({'username': user.get('username')})
        if count_users != 1:
            message=f"Usuário '{user.get('username')}' não encontrado."
            current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            return jsonify({
                'ACK': False,
                'message': message
            }), 400

        defaults ={'updated_at': datetime.utcnow() }
        
        update_data = user | defaults

        if request.json.get('username') == user_id:
            if user_has_profile(user_id,'user'):
                profile_user = {"profile":"user"}
            
            if user_has_profile(user_id,'sysadmin'):
                profile_user = {"profile":"sysadmin"}
                
            update_data = update_data | profile_user
        
        db.users.update_one({'username': update_data.get('username')},{"$set": update_data})
        
        user_profile = db.users.find_one({'username':update_data.get('username')})
        profile_data = json.loads(json.dumps(user_profile, default=lambda x: list(x) if isinstance(x, tuple) else str(x)))
    
    
    except Exception as e:
        message = f"{e}"
        current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message': message
        })

    message=f"Perfil do usuário {profile_data.get('username')} alterado com sucesso"
    current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: {message}")
    return jsonify({
        'ACK': True,
        'message': message,
        'data': [profile_data]
    })


@blueprint.route("/insert_profile", methods = ["POST"])
@cross_origin()
@access_token_required
@sysadmin_required
def insert_profile():

    try:        
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

        defaults ={
            'created_at': datetime.utcnow(),
            'profile': 'user',
            'updated_at': None,
            'deleted_at': None
        }

        insert_data = user | defaults
    
        db.users.insert_one(insert_data)

        user_profile = db.users.find_one({'username':insert_data.get('username')})
        profile_data = json.loads(json.dumps(user_profile, default=lambda x: list(x) if isinstance(x, tuple) else str(x)))
    
    except Exception as e:
        message = f"{e}"
        current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message': message
        })

    message=f"Usuário(a) '{insert_data.get('name')}' inserido com sucesso"
    current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: {message}")
    return jsonify({
        'ACK': True,
        'message': message,
        'data': [profile_data]
    })


@blueprint.route("/delete_profile", methods = ["POST"])
@cross_origin()
@access_token_required
@sysadmin_required
def delete_profile():
    user_id = request.cookies.get('user_id')

    user = dict(request.json)
    if request.json.get('username') == user_id:
        message=f"{user_id}, você não pode excluir o próprio perfil."
        current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message': message
        }), 400
    
    try:
        delete_data = {
                'username': user.get('username'),
                'deleted_at': datetime.utcnow()
            }

        db = get_conn('pessoa')

        user_profile = db.users.find_one({'username':delete_data.get('username')})
                   
        if user_profile == None:
            message=f"Usuário '{user.get('username')}' não encontrado."
            current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            return jsonify({
                'ACK': False,
                'message': message
            }), 400
        
        
        profile_data = json.loads(json.dumps(user_profile, default=lambda x: list(x) if isinstance(x, tuple) else str(x)))
        
        db.users.update_one({'username': delete_data.get('username')},{"$set": delete_data})

    
    except Exception as e:
        message = f"{e}"
        current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message': message
        })

    message=f"Perfil do usuário {profile_data.get('username')} excluído com sucesso (soft delete)"
    current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: {message}")
    return jsonify({
        'ACK': True,
        'message': message,
        'data': [profile_data]
    })


@blueprint.route("/purge_profile", methods = ["DELETE"])
@cross_origin()
@access_token_required
@sysadmin_required
def purge_profile():
    user_id = request.cookies.get('user_id')

    user = dict(request.json)
    if request.json.get('username') == user_id:
        message=f"{user_id}, você não pode excluir o próprio perfil."
        current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message': message
        }), 400
    
    try:

        db = get_conn('pessoa')

        user_profile = db.users.find_one({'username':user.get('username')})
                   
        if user_profile == None:
            message=f"Usuário '{user.get('username')}' não encontrado."
            current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            return jsonify({
                'ACK': False,
                'message': message
            }), 400
        
        
        profile_data = json.loads(json.dumps(user_profile, default=lambda x: list(x) if isinstance(x, tuple) else str(x)))
        
        db.users.delete_one({'username': user.get('username')})

    
    except Exception as e:
        message = f"{e}"
        current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message': message
        })

    message=f"Perfil do usuário {profile_data.get('username')} excluído com sucesso (purge)"
    current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: {message}")
    return jsonify({
        'ACK': True,
        'message': message,
        'data': [profile_data]
    })