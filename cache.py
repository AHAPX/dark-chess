import pickle

from redis import StrictRedis

import consts
import config
from helpers import get_queue_name, get_prefix


redis = StrictRedis(config.CACHE_HOST, config.CACHE_PORT, config.CACHE_DB)


def set_cache(key, data, time=None):
    _data = pickle.dumps(data)
    if time:
        redis.setex(key, time, _data)
    else:
        redis.set(key, _data)


def get_cache(key):
    value = redis.get(key)
    try:
        return pickle.loads(value)
    except:
        return value


def delete_cache(key):
    redis.delete(key)


def add_to_queue(token, prefix=''):
    redis.rpush(get_queue_name(prefix), token.encode())


def get_from_queue(prefix=''):
    value = redis.lpop(get_queue_name(prefix))
    try:
        return value.decode()
    except:
        return value


def get_from_any_queue(game_type):
    for limit in [p[1] for p in consts.TYPES.get(game_type, {}).get('periods', []).values()]:
        token = get_from_queue(get_prefix(game_type, limit))
        if token:
            return token, limit
    return None, None
