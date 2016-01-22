import config
from redis import StrictRedis


redis = StrictRedis(config.CACHE_HOST, config.CACHE_PORT)


def set_cache(key, data, time=None):
    if time:
        redis.setex(key, time, data)
    else:
        redis.set(key, data)


def get_cache(key):
    return redis.get(key)


def delete_cache(key):
    redis.delete(key)


def add_to_queue(token):
    redis.rpush('players_queue', token)
