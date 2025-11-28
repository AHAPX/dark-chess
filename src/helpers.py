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


def generate_token(short=False):
    token = uuid.uuid4().hex
    if short:
        return token[:config.TOKEN_SHORT_LENGTH]
    return token


def with_context(data):
    context = {
        'site_url': config.SITE_URL,
    }
    context.update(data)
    return context


def get_queue_name(prefix):
    return '{}_{}'.format(prefix, config.GAME_QUEUE_NAME)


def get_prefix(game_type, game_limit=None):
    return '{}-{}'.format(game_type, game_limit if game_limit is not None else '*')


def _get_request_json(request):
    """
    Try to read JSON data without raising BadRequest if payload is invalid.
    Flask's `request.json` property raises in that scenario, so prefer the
    `get_json(silent=True)` helper when available, but fall back to the legacy
    attribute for test doubles.
    """
    get_json = getattr(request, 'get_json', None)
    if callable(get_json):
        try:
            return get_json(silent=True)
        except TypeError:
            # Older Flask versions might not accept the silent kwarg.
            try:
                return get_json()
            except TypeError:
                return None
    return getattr(request, 'json', None)


def get_request_arg(request, name):
    json_payload = _get_request_json(request) or {}
    return request.form.get(name) or json_payload.get(name)
