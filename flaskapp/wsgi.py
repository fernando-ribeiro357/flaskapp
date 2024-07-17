import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/opt/app/")

from app import app 

application = app
