from os import getenv
from extensions.db import get_conn
from datetime import datetime

import requests, logging.config

from flask import ( Blueprint, 
                    jsonify,
                    make_response,
                    redirect,
                    render_template,
                    current_app,
                    request )

from extensions.token_utils import refresh_token_required, sysadmin_required

blueprint = Blueprint('views', __name__)


@blueprint.route("/",methods = ['GET','POST'])
# def index():
#     return render_template('index.html')
@blueprint.route("/login",methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        # processar o formulário
        payload = {
            'username': request.form.get('username'),
            'password': request.form.get('password')
        }
        resposta = None
        try:
            resposta = requests.post(f"{getenv('APP_URL')}/api/v1/auth",
                        json=payload)
            refresh_token = resposta.json()
            # { ACK: Bool, token: "aqui-evem-o-token" }            
            # return jsonify({'refresh_token': refresh_token})

        except Exception as e:
            message = f'erro login: {e}'
            current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            response = make_response(redirect("/login"))
            return response
        
        if refresh_token['ACK']:
            response = make_response(redirect("/profile"))
            response.set_cookie(key='token', value=refresh_token.get('token'), httponly=True)
            response.set_cookie(key='user_id', value=payload.get('username'), httponly=True)
            return response

    
    return render_template('login.html')


@blueprint.route("/profiles")
@refresh_token_required
@sysadmin_required
def get_profiles():
    # requisitar um token de acesso
    try:
        resposta_access = requests.get(
            f"{getenv('APP_URL')}/api/v1/auth/get_access_token",
            cookies=request.cookies)
        
        access_token = resposta_access.json()['token']
        
    # requisição para uma api que forneça os dados de profile
        resposta_profiles = requests.get(
            f"{getenv('APP_URL')}/api/v1/get_profiles", 
            headers={'Authorization': f'Bearer {access_token}'},
            cookies=request.cookies)
    
    # formatar os dados recebidos
        profiles = resposta_profiles.json()
        # return jsonify(profiles)

    except Exception as e:
        message = f'erro profile: {e}'
        current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        response = make_response(redirect("/"))
        return response
    
    current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: carregou dados de perfis")
    return render_template('profiles.html',context=profiles)



@blueprint.route("/profile")
@refresh_token_required
def get_profile():
    # requisitar um token de acesso
    try:
        resposta_access = requests.get(
            f"{getenv('APP_URL')}/api/v1/auth/get_access_token",
            cookies=request.cookies)
        
        access_token = resposta_access.json()['token']
        
    # requisição para uma api que forneça os dados de profile
        resposta_profile = requests.post(
            f"{getenv('APP_URL')}/api/v1/get_profile_data", 
            headers={'Authorization': f'Bearer {access_token}'},
            json={'user_id': request.cookies.get('user_id')})
    
    # formatar os dados recebidos
        profile_data = resposta_profile.json()
        
    except Exception as e:
        message = f'erro profile: {e}'
        current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        response = make_response(redirect("/"))
        return response
    
    current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: carregou dados de perfis")
    return render_template('profile.html',context=profile_data)
    

@blueprint.route("/user_profile")
@refresh_token_required
@sysadmin_required
def get_profile_user():
    # requisitar um token de acesso
    try:
        resposta_access = requests.get(
            f"{getenv('APP_URL')}/api/v1/auth/get_access_token",
            cookies=request.cookies)
        
        access_token = resposta_access.json()['token']
        
        user_id = request.args.get('user_id')
        if user_id == None:
            message = 'erro profile_user: Parâmetro não fornecido'
            current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            response = make_response(redirect("/"))
            return response    
    # requisição para uma api que forneça os dados de profile
        resposta_profile = requests.post(
            f"{getenv('APP_URL')}/api/v1/get_profile_data", 
            headers={'Authorization': f'Bearer {access_token}'},
            json={'user_id': user_id})
    
    # formatar os dados recebidos
        profile_data = resposta_profile.json()
        
    except Exception as e:
        message = f'erro profile: {e}'
        current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        response = make_response(redirect("/"))
        return response
    
    current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: carregou dados de perfis")
    return render_template('profile_update.html',context=profile_data)


@blueprint.route("/profile_insert",methods=['POST','GET'])
@refresh_token_required
@sysadmin_required
def profile_insert():
    if request.method == 'POST':
    # requisitar um token de acesso
        try:
            resposta_access = requests.get(
                f"{getenv('APP_URL')}/api/v1/auth/get_access_token",
                cookies=request.cookies)
            
            access_token = resposta_access.json()['token']
            
            date = datetime.now()
            
            user_data = {
                'username': request.form.get('username'),
                'name': request.form.get('name'),
                'email': request.form.get('email'),
                'password': request.form.get('password'),
                'profile': 'user',
                'created_at': date.strftime("%Y-%m-%d %H:%M:%S"),
                'updated_at': None
            }

            # requisição para uma api que forneça os dados de profile
            resposta_profile = requests.post(
                f"{getenv('APP_URL')}/api/v1/insert_profile", 
                headers={'Authorization': f'Bearer {access_token}'},
                cookies=request.cookies,
                json=user_data)
        
            # formatar os dados recebidos
            profile_data = resposta_profile.json()    
            # return jsonify({'perfil': profile_data})
            
        except Exception as e:
            message = f'erro insert: {e}'
            current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            response = make_response(redirect("/"))
            return response
        
        current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: Inseriu perfil {profile_data}")
        response = make_response(redirect("/profiles"))
        return response
        # return jsonify(profile_data)

    return render_template('profile_insert.html')
    

@blueprint.route("/profile_update",methods=['POST','GET'])
@refresh_token_required
@sysadmin_required
def profile_update():
    if request.method == 'POST':
    # requisitar um token de acesso
        try:
            resposta_access = requests.get(
                f"{getenv('APP_URL')}/api/v1/auth/get_access_token",
                cookies=request.cookies)
            
            access_token = resposta_access.json()['token']
            
            date = datetime.now()
                
            user_data = {
                'name': request.form.get('name'),
                'username': request.form.get('username'),
                'profile': request.form.get('profile'),
                'updated_at': date.strftime("%Y-%m-%d %H:%M:%S")
            }
            passwd = request.form.get('password')
            if passwd != "":
                user_data['password'] = passwd

            # requisição para uma api que forneça os dados de profile
            resposta_profile = requests.put(
                f"{getenv('APP_URL')}/api/v1/update_profile", 
                headers={'Authorization': f'Bearer {access_token}'},
                cookies=request.cookies,
                json=user_data)
        
            # formatar os dados recebidos
            profile_data = resposta_profile.json()    
            
            
        except Exception as e:
            message = f'erro update: {e}'
            current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            response = make_response(redirect("/"))
            return response
        
        current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: Atualizou o perfil {profile_data}")
        response = make_response(redirect("/profiles"))
        return response
        # return jsonify(profile_data)

    username = request.args.get("user_id")
    db = get_conn('pessoa')
    user = db.users.find({'username': username})
    
    return render_template('profile_update.html',context=user)