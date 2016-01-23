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


def invertColor(color):
    if color == WHITE:
        return BLACK
    return WHITE


def encryptPassword(password):
    return md5(md5(password).hexdigest() + config.PASSWORD_SALT).hexdigest()


def generateToken():
    return str(uuid.uuid4())
