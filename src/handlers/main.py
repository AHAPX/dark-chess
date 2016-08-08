import sys
import traceback
import logging

from flask import Blueprint

from serializers import send_message
from decorators import use_cache
import config


logger = logging.getLogger(__name__)

bp = Blueprint('main', __name__, url_prefix='/v1/')


@bp.route('/')
@use_cache()
def _index():
    return send_message('welcome to dark chess')
