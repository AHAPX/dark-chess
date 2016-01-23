from functools import wraps

from flask import request

import errors
from models import User
from cache import get_cache
from serializers import send_error
from game import Game


def authenticated(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = (request.json or {}).get('auth') or \
            request.values.get('auth') or \
            request.cookies.get('auth')

        if token is not None:
            user_id = get_cache(token)
            if user_id:
                try:
                    user = User.get(pk=user_id)
                except User.DoesNotExist:
                    pass
                else:
                    request.user = user
                    request.auth = token
                    return f(*args, **kwargs)
        return send_error('not authorized')
    return decorated


def with_game(f):
    @wraps(f)
    def decorated(token, *args, **kwargs):
        try:
            game = Game.load_game(token)
        except errors.GameNotFoundError as exc:
            return send_error(exc.message)
        return f(game, *args, **kwargs)
    return decorated
