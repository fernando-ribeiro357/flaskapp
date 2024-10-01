import datetime, logging.config
from os import getenv
from functools import wraps
from .db import get_conn

from flask import (jsonify,
                   request, 
                   flash,
                   make_response,
                   redirect,
                   current_app)


def user_has_profile(username, profile):
    try:
        # busca usuario no banco e verifica se possui perfil fornecido"
        db = get_conn('pessoa')    
        user = db.users.find_one({'username': username, "profile": profile})
        if user == None:
            return False
        
        else:
            return True

    except Exception as e:
        return False    

def is_sysadmin(username):
    return user_has_profile(username,'sysadmin')

def sysadmin_owner_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        # Busca o user_id e profile nos cookies
        user_id = request.cookies.get('user_id')        
        username = request.args.get('username')
        if username == None:
            username = request.form.get('username')
        
        if username == None:
            username = request.json.get('username')
        
        if user_id == None:
            message = 'user_id "None": Usuário não logado'
            current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            flash(message)
            return make_response(redirect("/"))
        
        if username == user_id:
            # Permite executar se a alteração for executada pelo próprio usuário
            message = f"O(A) usuário(a) '{user_id}' é dono do perfil '{username}'"
            current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            return fn(*args,**kwargs)
        
        else:        
            # Ou permite executar se a alteração for executada por usuário perfil 'sysadmin' 
            if is_sysadmin(user_id) == False:
                message = f"O(A) usuário(a) '{user_id}' não possui perfil de sysadmin e não é dono do perfil '{username}'"
                current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
                flash(message)
                return make_response(redirect("/"))

        return fn(*args,**kwargs)
    return wrapped

def sysadmin_required(fn):
    @wraps(fn)
    def sysadmin_required_wrap(*args, **kwargs):
    # Busca o user_id e profile nos cookies
        user_id = request.cookies.get('user_id')        

        if user_id == None:
            message = 'Usuário não logado'
            current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            flash(message)
            return make_response(redirect("/"))
       
        if is_sysadmin(user_id) == False:
                message = f"Usuário(a) '{user_id}' não possui o perfil 'sysadmin'"
                current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
                flash(message)
                return make_response(redirect("/"))

        return fn(*args,**kwargs)
    return sysadmin_required_wrap
