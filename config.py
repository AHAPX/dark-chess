from playhouse.sqlite_ext import SqliteExtDatabase

DB = SqliteExtDatabase('/tmp/dark_chess.db')

DEBUG = False

HOST = '0.0.0.0'
PORT = 38599

CACHE_HOST = 'localhost'
CACHE_PORT = 6379

VERIFICATION_PERIOD = 10 * 60
VERIFICATION_TIME = 2 * 60 * 60
SESSION_TIME = 24 * 60 * 60

PASSWORD_SALT = ''


try:
    from config_local import *
except:
    pass
