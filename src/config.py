# db config
from playhouse.sqlite_ext import SqliteExtDatabase
DB = SqliteExtDatabase('/tmp/dark_chess.db')

# development mode
DEBUG = False

# url
SITE_URL = 'http://localhost'
VERIFY_URL = '/#/auth/verify/'
RECOVER_URL = '/#/auth/recover/'

# dark-chess server config
HOST = '0.0.0.0'
PORT = 38599

# cache config
CACHE_HOST = 'localhost'
CACHE_PORT = 6379
CACHE_DB = 0

# websocket config
WS_BROKER_HOST = CACHE_HOST
WS_BROKER_PORT = CACHE_PORT
WS_BROKER_CHANNEL = 'ws-channel'
WS_BROKER_DB = 1

# smtp config
SMTP_BROKER_HOST = CACHE_HOST
SMTP_BROKER_PORT = CACHE_PORT
SMTP_BROKER_CHANNEL = 'smtp-channel'
SMTP_BROKER_DB = 1

# times and periods
VERIFICATION_PERIOD = 10 * 60
VERIFICATION_TIME = 2 * 60 * 60
SESSION_TIME = 24 * 60 * 60
CACHE_MAX_TIME = 24 * 60 * 60
RESET_PERIOD = 5 * 60
RESET_TIME = 30 * 60

# password and tokens config
PASSWORD_SALT = ''
TOKEN_SHORT_LENGTH = 10

# game config
GAME_QUEUE_NAME = 'players_queue'

# chat config
MAX_COUNT_MESSAGES = 50
DEFAULT_COUNT_MESSAGES = 10
MAX_LENGTH_MESSAGE = 100

# load local config if exists
try:
    from config_local import *
except:
    pass
