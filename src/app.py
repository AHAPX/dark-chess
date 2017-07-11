import sys
import traceback
from flask import Flask

from handlers.v1.auth import bp as bp_auth
from handlers.v1.main import bp as bp_main
from handlers.v1.game import bp as bp_game
from handlers.v1.chat import bp as bp_chat
from handlers.v2.urls import bp as bp_v2
from handlers.v2.urls import bp_auth as bp_auth_v2
from errors import BaseException
from loggers import logger


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')

app.register_blueprint(bp_main)
app.register_blueprint(bp_auth)
app.register_blueprint(bp_game)
app.register_blueprint(bp_chat)
app.register_blueprint(bp_v2)
app.register_blueprint(bp_auth_v2)


@app.errorhandler(Exception)
def all_exception_handler(error):
    if isinstance(error, BaseException):
        from serializers import send_error
        return send_error(error.message)
    try:
        logger.critical('\n'.join(traceback.format_tb(sys.exc_info()[2])))
    except:
        pass
    if app.config['DEBUG']:
        raise error.with_traceback(sys.exc_info()[2])
    return 'critical server error', 500
