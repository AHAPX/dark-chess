from functools import wraps

from flask import request

import config
import errors
from models import User
from cache import get_cache, set_cache, get_cache_func_name
from serializers import send_error, send_message
from format import format


def authenticated(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = (request.json or {}).get('auth') or \
            request.values.get('auth') or \
            request.cookies.get('auth')
        request.user = None
        request.auth = None
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
    return decorator


def login_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if hasattr(request, 'user') and request.user:
            return f(*args, **kwargs)
        return send_error('not authorized')
    return decorator


def with_game(f):
    @wraps(f)
    def decorator(token, *args, **kwargs):
        from game import Game

        try:
            game = Game.load_game(token)
        except errors.GameNotStartedError as exc:
            return send_message(exc.message)
        except errors.GameNotFoundError as exc:
            return send_error(exc.message)
        return f(game, *args, **kwargs)
    return decorator


def formatted(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        results = f(*args, **kwargs)
        if isinstance(results, dict):
            return {k: format(v) for k, v in results.items()}
        if isinstance(results, (list, tuple)):
            return type(results)(format(v) for v in results)
        return format(results)
    return decorator


def use_cache(time=config.CACHE_MAX_TIME, name=None):
    def wrapper(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            fn = name if name else '.'.join([f.__module__, f.__name__])
            cache_name = get_cache_func_name(fn, *args, **kwargs)
            results = get_cache(cache_name)
            if results is not None:
                return results
            results = f(*args, **kwargs)
            set_cache(cache_name, results, time)
            return results
        return decorator
    return wrapper


def validated(validator):
    def wrapper(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            try:
                val = validator(request)
            except errors.ValidationError as exc:
                return send_error(exc.message)
            if not val.is_valid():
                return send_error(val.get_error())
            return f(data=val.cleaned_data, *args, **kwargs)
        return decorator
    return wrapper
