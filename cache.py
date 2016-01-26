import config
from redis import StrictRedis


redis = StrictRedis(config.CACHE_HOST, config.CACHE_PORT)


def set_cache(key, data, time=None):
    if time:
        redis.setex(key, time, data)
    else:
        redis.set(key, data)


def get_cache(key):
    value = redis.get(key)
    try:
        return value.decode()
    except:
        return value


def delete_cache(key):
    redis.delete(key)


def add_to_queue(token):
    redis.rpush(config.GAME_QUEUE_NAME, token.encode())


def get_from_queue():
    value = redis.lpop(config.GAME_QUEUE_NAME)
    try:
        return value.decode()
    except:
        return value
