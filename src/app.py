import sys
import traceback
import logging

from flask import Flask

from handlers.auth import bp as bp_auth
from handlers.main import bp as bp_main
from handlers.game import bp as bp_game
from handlers.chat import bp as bp_chat
from errors import BaseException


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')

app.register_blueprint(bp_main)
app.register_blueprint(bp_auth)
app.register_blueprint(bp_game)
app.register_blueprint(bp_chat)

logger = logging.getLogger(__name__)


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
