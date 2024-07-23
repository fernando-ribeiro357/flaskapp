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
    <h3>Autenticação em <a href="http://localhost:8000/api/v1/auth">http://localhost:8000/api/v1/auth</a></h3>
    <p>TODO:</p>
    <ul>
        <li>Documentação swagger</li>
    </ul>
    </body>
    </html>
    '''


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
