import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/wsgi/flaskapp/flaskapp/")

from app import app as application
application.secret_key = 's80omOYQ2u3rS36lshZZFoDTUA6M4D2X6VpukP7aJEqknPhgIGDn5ds0h9x3vKI4'