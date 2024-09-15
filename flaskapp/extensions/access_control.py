import datetime, logging.config
from os import getenv
from functools import wraps
from .db import get_conn

from flask import jsonify, request, current_app


def user_has_profile(username, profile):
    
    try:
        # busca usuario no banco e verifica se possui perfil fornecido"
        db = get_conn('pessoa')    
        user = db.users.find_one({'username': username, "profile": profile})
        if user == None:
            message = f"Usuário(a) '{username}' não encontrado(a) ou não possui perfil '{profile}"
            current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            return False
        
        else:
            message = f"Usuário(a) '{username}' possui o perfil '{profile}'"
            current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            return True

    except Exception as e:
        message = f"Erro user_has_profile: {e}"
        current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return False    



def sysadmin_owner_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        # Busca o user_id e profile nos cookies
        user_id = request.cookies.get('user_id')        
        username = request.json.get('username')
        if user_id == None:
            message = 'user_id "None": Usuário não logado'
            current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            return jsonify({
                'ACK': False,
                'message':message
            })
        
        if request.method == 'PUT' and username == user_id:
            # Permite executar se o método for PUT e a alteração for executada pelo próprio usuário
            return fn(*args,**kwargs)        
        
        if user_has_profile(user_id,'sysadmin') == False:
                message = f"O(A) usuário(a) '{user_id}' não possui perfil de sysadmin e não é dono do perfil '{username}'. (perfil: {user_profile})"
                current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
                return jsonify({
                    'ACK': False,
                    'message':message
                })        

        return fn(*args,**kwargs)
    return wrapped


def sysadmin_required(fn):
    @wraps(fn)
    def sysadmin_required_wrap(*args, **kwargs):
    # Busca o user_id e profile nos cookies
        user_id = request.cookies.get('user_id')        

        if user_id == None:
            message = f'user_id "{user_id}": Usuário não logado'
            current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            return jsonify({
                'ACK': False,
                'message':message
            })
       
        if user_has_profile(user_id,'sysadmin') == False:
                message = f"Usuário(a) '{user_id}' não possui o perfil 'sysadmin'"
                current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
                return jsonify({
                    'ACK': False,
                    'message':message
                })
        
        return fn(*args,**kwargs)
    return sysadmin_required_wrap
