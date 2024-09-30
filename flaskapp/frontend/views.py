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
                    flash,
                    request )

from api.auth import is_logged, hash_password
from extensions.token_utils import token_required
from extensions.access_control import  (sysadmin_required,
                                        sysadmin_owner_required, 
                                        is_sysadmin)

blueprint = Blueprint('views', __name__)

@blueprint.route("/sair",methods = ['GET'])
def sair():
    flash("Usuário deslogado!")
    response = make_response(redirect("/"))
    response.delete_cookie("token")
    response.delete_cookie("user_id")
    return response

@blueprint.route("/",methods = ['GET'])
def home():
    if is_logged():
        token = request.cookies.get('token')
        user_id = request.cookies.get('user_id')
        
        response = make_response(redirect("/tasks/add_get"))
        response.headers['Authorization'] = f"Bearer {token}"
        response.set_cookie(key='token', value=token, httponly=True)
        response.set_cookie(key='user_id', value=user_id, httponly=True)
        return response
    
    else:
        return make_response(redirect('/login'))



@blueprint.route("/login",methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        # processar o formulário
        payload = {
            'username': request.form.get('username'),
            'password': request.form.get('password')
        }
        get_auth = None
        try:
            get_auth = requests.post(f"{getenv('APP_URL')}/api/v1/auth",
                        json=payload,
                        cookies=request.cookies)
            resposta = get_auth.json()

        except Exception as e:
            message = f'erro login: {e}'
            current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            flash(message)
            retorno = make_response(redirect('/login'))
            return retorno
        
        if resposta.get('ACK'):
            token = resposta.get('token')
            user = resposta.get('user')
            return jsonify(user)
            # response = make_response(redirect("/tasks/add_get"))
            # response.headers['Authorization'] = f"Bearer {token}"
            # response.set_cookie(key='token', value=token, httponly=True)
            # response.set_cookie(key='user_id', value=payload.get('username'), httponly=True)
            # return response
        else:
            message = resposta.get('message')
            flash(message)
            retorno = make_response(redirect('/login'))
            return retorno

    
    return render_template('login.html')


@blueprint.route("/profile", methods = ['GET'])
@token_required
def get_profile():
    try:
        token = request.cookies.get('token')
        user_id = request.cookies.get('user_id')
        
        if (token == None):
            message = 'Token Nulo'
            current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            flash(message)
            return make_response(redirect("/"))

    # requisição para uma api que forneça os dados de profile
        resposta_profile = requests.post(
            f"{getenv('APP_URL')}/api/v1/get_profile_data", 
            headers={'Authorization': f'Bearer {token}'},
            json={'user_id': user_id},
            cookies=request.cookies)
    
    # formatar os dados recebidos
        profile_data = resposta_profile.json()
        if profile_data.get('ACK') == False:
            message = profile_data.get('message')
            current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            flash(message)
            return make_response(redirect("/"))
        
    except Exception as e:
        message = f'erro profile: {e}'
        current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        flash(message)
        response = make_response(redirect("/"))
        return response
    
    current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: carregou dados do perfil")
    return render_template('profile.html',context=profile_data.get('data')[0],sysadmin=is_sysadmin(request.cookies.get('user_id')))
    

@blueprint.route("/profiles", methods = ['GET'])
@token_required
@sysadmin_required
def get_profiles():
    try:
        token = request.cookies.get('token')
        if (token == None):
            message = 'Token Nulo'
            current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            flash(message)
            return make_response(redirect("/"))
                
    # requisição para uma api que forneça os dados de profile
        resposta_profiles = requests.get(
            f"{getenv('APP_URL')}/api/v1/get_profiles", 
            headers={'Authorization': f'Bearer {token}'},
            cookies=request.cookies)
    
    # formatar os dados recebidos
        profiles = resposta_profiles.json()
        

    except Exception as e:
        message = f'erro profiles: {e}'
        current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        flash(message)
        response = make_response(redirect("/"))
        return response
    
    
    user_id = request.cookies.get('user_id')
    sysadmin = is_sysadmin(user_id)
    message = "Carregou dados de perfis"
    current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: {message}")
    return render_template('profiles.html',context=profiles.get('data'),sysadmin=sysadmin)



@blueprint.route("/user_profile", methods = ['GET'])
@token_required
@sysadmin_owner_required
def get_profile_user():
    # requisitar um token de acesso
    try:
        user_id = request.args.get('user_id')
        token = request.cookies.get('token')
        if user_id == None:
            message = 'Parâmetro não fornecido'
            current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            flash(message)
            response = make_response(redirect("/"))
            return response    
    # requisição para uma api que forneça os dados de profile
        resposta_profile = requests.post(
            f"{getenv('APP_URL')}/api/v1/get_profile_data", 
            headers={'Authorization': f'Bearer {token}'},
            json={'user_id': user_id},
            cookies=request.cookies)
    
    # formatar os dados recebidos
        profile_data = resposta_profile.json()
        
    except Exception as e:
        message = f'erro profile: {e}'
        current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        flash(message)
        response = make_response(redirect("/"))
        return response
    
    current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: carregou dados de perfis")
    return render_template('profile_update.html',context=profile_data.get('data')[0],sysadmin=is_sysadmin(request.cookies.get('user_id')))


@blueprint.route("/profile_insert",methods=['POST','GET'])
@token_required
@sysadmin_required
def profile_insert():
    if request.method == 'POST':
    # requisitar um token de acesso
        try:
            
            token = request.cookies.get('token')
                        
            date = datetime.now()
            
            user_data = {
                'username': request.form.get('username'),
                'name': request.form.get('name'),
                'email': request.form.get('email'),
                'password': hash_password(request.form.get('password')),
                'profile': 'user',
                'created_at': date.strftime("%Y-%m-%d %H:%M:%S"),
                'updated_at': None
            }

            # requisição para uma api que forneça os dados de profile
            resposta_profile = requests.post(
                f"{getenv('APP_URL')}/api/v1/insert_profile", 
                headers={'Authorization': f'Bearer {token}'},
                cookies=request.cookies,
                json=user_data)
        
            # formatar os dados recebidos
            profile_data = resposta_profile.json()    
            # return jsonify({'perfil': profile_data})
            
        except Exception as e:
            message = f'erro insert: {e}'
            current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
            flash(message)
            response = make_response(redirect("/"))
            return response
        
        message = f"{profile_data.get('message')}"
        current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        response = make_response(redirect("/profiles"))
        return response
        # return jsonify(profile_data)

    return render_template('profile_insert.html',sysadmin=is_sysadmin(request.cookies.get('user_id')))
    

@blueprint.route("/profile_update",methods=['POST','GET'])
@token_required
@sysadmin_owner_required
def profile_update():
    if request.method == 'POST':
    # requisitar um token de acesso
        try:
            cookies=request.cookies
            token = cookies.get('token')
            
            date = datetime.now()
                
            user_data = {
                'name': request.form.get('name'),
                'username': request.form.get('username'),
                'profile': request.form.get('profile'),
                'updated_at': date.strftime("%Y-%m-%d %H:%M:%S")
            }
            passwd = request.form.get('password')
            if passwd != "":
                user_data['password'] = hash_password(passwd)

            # requisição para uma api que forneça os dados de profile
            resposta_profile = requests.patch(
                f"{getenv('APP_URL')}/api/v1/update_profile", 
                headers={'Authorization': f'Bearer {token}'},
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
    response = render_template('profile_update.html',context=user,sysadmin=is_sysadmin(username))
    response.headers['Content-Type'] = "text/html"
    return response