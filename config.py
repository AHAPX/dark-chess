# db config
from playhouse.sqlite_ext import SqliteExtDatabase
DB = SqliteExtDatabase('/tmp/dark_chess.db')

# development mode
DEBUG = False

# url
SITE_URL = 'http://localhost'

# dark-chess server config
HOST = '0.0.0.0'
PORT = 38599

# cache config
CACHE_HOST = 'localhost'
CACHE_PORT = 6379
CACHE_DB = 0

# websocket config
WS_HOST = '0.0.0.0'
WS_PORT = 9998
WS_CHANNEL = 'ws-channel'

# times and periods
VERIFICATION_PERIOD = 10 * 60
VERIFICATION_TIME = 2 * 60 * 60
SESSION_TIME = 24 * 60 * 60
CACHE_MAX_TIME = 24 * 60 * 60

# password and tokens config
PASSWORD_SALT = ''
TOKEN_SHORT_LENGTH = 10

# email config
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_USERNAME = None
MAIL_PASSWORD = None
DEFAULT_MAIL_SENDER = 'info@dark-chess'
MAIL_SUBJECT_PREFIX = 'dask-chess: '

# celery config
CELERY_BROKER_URL = 'redis://localhost:6379/1'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'

# game config
GAME_QUEUE_NAME = 'players_queue'


# load local config if exists
try:
    from config_local import *
except:
    pass
