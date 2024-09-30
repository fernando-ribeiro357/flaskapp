import logging.config
import os
from os import getenv

from flask import Flask, jsonify

from dotenv import load_dotenv

# blueprints
from api.auth import blueprint as auth
from api.profile import blueprint as profile
from frontend.views import blueprint as views
from frontend.todolist import blueprint as todolist

logging.config.fileConfig('logging.ini')

load_dotenv()

app = Flask(__name__)

# blueprints
app.register_blueprint(auth)
app.register_blueprint(profile)
app.register_blueprint(views)
app.register_blueprint(todolist)
app.secret_key = getenv('SECRET_KEY')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
