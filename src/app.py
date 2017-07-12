import sys
import traceback
from flask import Flask

from handlers.v1.auth import bp as bp_auth_v1
from handlers.v1.main import bp as bp_main_v1
from handlers.v1.game import bp as bp_game_v1
from handlers.v1.chat import bp as bp_chat_v1
from handlers.v2.urls import bp_main, bp_auth, bp_chat, bp_game
from errors import BaseException
from loggers import logger


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')

# version 1, depricated
app.register_blueprint(bp_main_v1)
app.register_blueprint(bp_auth_v1)
app.register_blueprint(bp_game_v1)
app.register_blueprint(bp_chat_v1)

# current API
app.register_blueprint(bp_main)
app.register_blueprint(bp_auth)
app.register_blueprint(bp_chat)
app.register_blueprint(bp_game)


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
