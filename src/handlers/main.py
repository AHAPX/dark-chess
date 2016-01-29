import sys
import traceback
import logging

from serializers import send_message
from app import app
from decorators import use_cache
import config


logger = logging.getLogger(__name__)


@app.route('/')
@use_cache()
def _index():
    return send_message('welcome to dark chess')


@app.errorhandler(Exception)
def all_exception_handler(error):
    try:
        logger.critical('\n'.join(traceback.format_tb(sys.exc_info()[2])))
    except:
        pass
    if config.DEBUG:
        raise error.with_traceback(sys.exc_info()[2])
    return 'critical server error', 500
