
from os import getenv

import pymongo

def get_conn(database):
    client = None

    try:
        client = pymongo.MongoClient(getenv('MONGO_URL'))
    except Exception as e:
        return {
            'ACK': False,
            'message': 'Não foi possível se conectar ao banco de dados'
        }
    
    return client.get_database(database)