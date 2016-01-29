import datetime


def _datetime(value):
    return value.strftime('%Y-%m-%d %H:%M:%S')


def _float(value):
    return round(value, 1)


FORMATS = {
    datetime.datetime: _datetime,
    float: _float
}


def format(value):
    try:
        return FORMATS.get(type(value), lambda a: a)(value)
    except:
        return value


ARGS_FORMATS = {
    str: lambda a: str(a),
    float: lambda a: float(a),
    int: lambda a: int(a),
}


def get_argument(value, _type):
    return ARGS_FORMATS.get(_type, lambda a: _type(a))(value)
