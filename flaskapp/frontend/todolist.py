from bson.objectid import ObjectId
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
                                        is_sysadmin)

blueprint = Blueprint(
    'todolist',
    __name__,
    url_prefix='/tasks')

# Function to add a task to the to-do list and show tasks
@blueprint.route('/add_get',methods=['GET','POST'])
@token_required
def get_add_tasks():
    
    db = get_conn('todolist')
    if request.method == 'POST':
        task_data = {'task': request.form.get('task')}
        task = dict(task_data)
        db.tasks.insert_one(task_data)
        message="Tarefa inserida na lista"
        current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        response = make_response(redirect('/tasks/add_get'))
        return response

    tarefas = [{'id':u['_id'],'task': u['task']} for u in db.tasks.find()]
    message="Carregou a lista de tarefas"
    current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: {message}")
    return render_template('tasks.html',tasklist=tarefas,l=len(tarefas),sysadmin = is_sysadmin(request.cookies.get('user_id')))


# Function to clear the to-do list
@token_required
@blueprint.route('/clear')
def clear_list():
    db = get_conn('todolist')
    db.tasks.delete_many({});
    message = "Lista de tarefas apagada"
    flash(message)
    current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: {message}")
    response = make_response(redirect('/tasks/add_get'))
    return response



# Function to remove a task from the to-do list
@token_required
@blueprint.route('/del',methods=['GET'])
def remove_task():
    db = get_conn('todolist')
    task_id = request.args.get('id')
    try:
        db.tasks.delete_one({'_id': ObjectId(task_id)});
    except Exception as e:
        message = f'Erro ao excluir a tarefa {task_id}: {e}'
        current_app.logger.critical(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        flash(message)
        retorno = make_response(redirect('/tasks/add_get'))
        return retorno


    message = f"Tarefa id {task_id} apagada"
    current_app.logger.info(f"{request.remote_addr.__str__()} - {__name__}: {message}")
    response = make_response(redirect('/tasks/add_get'))
    return response