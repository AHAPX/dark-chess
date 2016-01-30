import datetime


def _datetime(value, **kwargs):
    return value.strftime('%Y-%m-%d %H:%M:%S')


def _float(value, **kwargs):
    return round(value, 1)


def _dict(value, level=2, **kwargs):
    if level > 0:
        return {k: format(v, level - 1) for k, v in value.items()}
    return value


def _list(value, level=2, **kwargs):
    if level > 0:
        return [format(x, level - 1) for x in value]
    return value


def _tuple(value, level=2, **kwargs):
    if level > 0:
        return tuple([format(x, level - 1) for x in value])
    return value


FORMATS = {
    datetime.datetime: _datetime,
    float: _float,
    dict: _dict,
    list: _list,
    tuple: _tuple,
}


def format(value, level=2):
    try:
        return FORMATS.get(type(value), lambda a: a)(value, level=level)
    except:
        return value


ARGS_FORMATS = {
    str: lambda a: str(a),
    float: lambda a: float(a),
    int: lambda a: int(a),
}


def get_argument(value, _type):
    return ARGS_FORMATS.get(_type, lambda a: _type(a))(value)
