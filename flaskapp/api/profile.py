import logging.config
from flask import Blueprint, jsonify, request, current_app

from extensions.token_utils import (jwt_required)
from extensions.db import get_conn

blueprint = Blueprint('profile',
                      __name__,
                      url_prefix='/api/v1')

@blueprint.route("/get_profile_data",methods=['POST'])
@jwt_required
def get_profile_data():
    db = get_conn('pessoa')
    user_id = request.json.get('user_id')

    try:
        profile_data = [
            {
                'full_name': u['name'],
                'profile': u['profile'],
                'email': u['email'],
                'registration_date': u['registration_date']
            } for u in db.users.find({'email':user_id})
        ]
    
    except Exception as e:
        message = f"erro get_profile_data: {e}"
        current_app.logger.warning(f"{request.remote_addr.__str__()} - {__name__}: {message}")
        return jsonify({
            'ACK': False,
            'message': message
        })
    
    return jsonify(profile_data[0])

