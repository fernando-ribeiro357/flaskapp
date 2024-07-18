from os import getenv

import requests, logging.config

from flask import ( Blueprint, 
                    jsonify,
                    make_response,
                    redirect,
                    render_template,
                    current_app,
                    request )

from extensions.token_utils import refresh_token_required

blueprint = Blueprint('views', __name__)

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
    return render_template('index.html',context=profile_data)
    

@blueprint.route("/outra_rota")
@refresh_token_required
def outra_rota():
    return jsonify({'ACK': True, 'message': 'Outra área restrita aqui'})