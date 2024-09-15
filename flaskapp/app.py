import logging.config
import os
from os import getenv

from flask import Flask, jsonify

from dotenv import load_dotenv

# blueprints
from api.auth import blueprint as auth
from api.profile import blueprint as profile

logging.config.fileConfig('logging.ini')

load_dotenv()

app = Flask(__name__)

# blueprints
app.register_blueprint(auth)
app.register_blueprint(profile)


@app.route("/")
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>FINUX System</title>
    </head>
    <body>
    <h1>Somente API</h1>
    <h3>Autenticação:</h3>
    <p>Enviar POST json {'username': 'seu-login-aqui', 'password':'sua-senha-aqui'} para http://localhost:8000/api/v1/auth</p>
    <p>Em processo:</p>
    <ul>Documentação swagger
        <li>/auth</li>
        <li>/auth/get_access_token</li>
        <li>/get_profile_data</li>
        <li>/get_profiles</li>
    </ul>
        
    </body>
    </html>
    '''


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
