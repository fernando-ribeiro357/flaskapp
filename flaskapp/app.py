import logging.config
import os
from os import getenv

from flask import Flask, jsonify, render_template

from dotenv import load_dotenv

# blueprints
from api.auth import blueprint as auth
from api.profile import blueprint as profile
from frontend.views import blueprint as views

logging.config.fileConfig('logging.ini')

load_dotenv()

app = Flask(__name__)

# blueprints
app.register_blueprint(auth)
app.register_blueprint(profile)
app.register_blueprint(views)


@app.route("/")
def index():
    return ''' 
    <h1>Index</h1>
    <ul>
        <li><a href="/login">Login</a></li>
        <li><a href="/profile">Perfil</a></li>
    </ul>
    '''

@app.route("/teste_login")
def teste_login():
    return render_template('login.html')

@app.route("/teste_profile")
def teste_profile():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
