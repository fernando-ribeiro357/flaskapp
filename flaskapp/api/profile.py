import logging.config
from datetime import datetime

from flask import Blueprint, jsonify, request, current_app

from extensions.token_utils import (access_token_required)
from extensions.access_control import (sysadmin_required, sysadmin_owner_required, user_has_profile)
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
        'message': 'Perfis buscados com sucesso',
        'data': profiles_data
    })

@blueprint.route("/get_profile_data")
@access_token_required
def get_profile_data():

    user_id = request.cookies.get('user_id')

    if user_id == None:
        message = f"erro user_id: {user_id}. Realize login novamente."
        current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message': message
        })
        
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
        'message': 'Perfil buscado com sucesso',
        'data': profile_data
    })


@blueprint.route("/update_profile", methods = ["PUT"])
@access_token_required
@sysadmin_owner_required
def update_profile():
    user_id = request.cookies.get('user_id')
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

    try:        
        profile_data = [
            {
                'name': u['name'],
                'username': u['username'],
                'profile': u['profile'],
                'email': u['email'],
                'password': u['password'],
                'created_at': u['created_at'],
                'updated_at': u['updated_at']
            } for u in db.users.find({'username':update_data.get('username')})
        ]
    
    except Exception as e:
        message = f"{e}"
        current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message': message
        })

    message=f"Perfil do usuário {profile_data[0].get('username')} alterado com sucesso"
    current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: {message}")
    return jsonify({
        'ACK': True,
        'message': message,
        'data': profile_data
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

    defaults ={
        'created_at': datetime.utcnow(),
        'profile': 'user',
        'updated_at': None,
        'deleted_at': None
    }

    insert_data = user | defaults
    
    db.users.insert_one(insert_data)

    try:        
        profile_data = [
            {
                'name': u['name'],
                'username': u['username'],
                'profile': u['profile'],
                'email': u['email'],
                'password': u['password'],
                'created_at': u['created_at'],
                'updated_at': u['updated_at']
            } for u in db.users.find({'username':insert_data.get('username')})
        ]
    
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
        'data': profile_data
    })
