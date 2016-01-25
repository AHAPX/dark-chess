import uuid
from hashlib import md5

from consts import WHITE, BLACK
import config


def onBoard(x, y):
    if 1 <= x <= 8 and 1 <= y <= 8:
        return True
    return False


def pos2coors(x, y):
    if not (isinstance(x, int) and isinstance(y, int)):
        raise TypeError
    if not onBoard(x, y):
        raise ValueError
    return '{}{}'.format('abcdefgh'[x - 1], y)


def coors2pos(coors):
    if len(coors) != 2:
        raise ValueError
    x, y = coors[0].lower(), int(coors[1])
    return ('abcdefgh'.index(x) + 1, y)


def invert_color(color):
    if color == WHITE:
        return BLACK
    return WHITE


def encrypt_password(password):
    pass_md5 = md5(password.encode()).hexdigest()
    return md5((pass_md5 + config.PASSWORD_SALT).encode()).hexdigest()


def generate_token():
    return str(uuid.uuid4())


def with_context(data):
    context = {
        'site_url': config.SITE_URL,
    }
    context.update(data)
    return context
