import datetime

from flask import Flask, request, make_response
from validate_email import validate_email

import config
import errors
from serializers import send_data, send_message, send_error
from decorators import authenticated, with_game
from models import User
from cache import delete_cache, add_to_queue
from helpers import generateToken


app = Flask(__name__)


@app.route('/')
def index():
    return send_message('welcome to dark chess')


@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')
    if User.select().where(User.username == username).count():
        return send_error('username is already in use')
    if len(password) < 8:
        return send_error('password must be at least 8 characters')
    if email:
        if not validate_email(email):
            return send_error('email is not valid')
        if User.select().where(User.email == email).count():
            return send_error('email is already in use')
    User.add(username, password, email)
    return send_message('registration successful')


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    token = User.authenticate(username, password)
    if token:
        response = make_response(send_data({'auth': token}))
        expire_date = datetime.datetime.now() + datetime.timedelta(seconds=config.SESSION_TIME)
        response.set_cookie('auth', token, expires=expire_date)
        return response
    return send_error('username or password is incorrect')


@app.route('/logout')
@authenticated
def logout():
    delete_cache(request.auth)
    response = make_response(send_message('logout successfully'))
    response.set_cookie('auth', expires=0)
    return response


@app.route('/game/new')
def new_game():
    token = generateToken()
    add_to_queue(token)
    return send_data({'game': token})


@app.route('/game/info/<token>')
@with_game
def game_info(game):
    return game.get_board()


@app.route('/game/move/<token>/<move>')
@with_game
def game_move(game, move):
    moves = move.split('-')
    if len(moves) == 2:
        return game.move(*moves)
    return send_error('move format must be like e2-e4')
