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
