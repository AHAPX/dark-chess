import datetime

from flask import request, make_response
from validate_email import validate_email

import config
from serializers import send_data, send_message, send_error, send_success
from decorators import authenticated, with_game
from models import User
from cache import delete_cache, add_to_queue
from helpers import generateToken
from app import app
from mail import send_mail_template


@app.route('/')
def index():
    return send_message('welcome to dark chess')


@app.route('/auth/register', methods=['POST'])
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
    user = User.add(username, password, email)
    if email:
        token = user.get_verification()
        data = {
            'username': username,
            'token': token,
        }
        send_mail_template('registration', [email], data=data)
    return send_message('registration successful')


@app.route('/auth/verification/')
@authenticated
def get_verification():
    try:
        token = request.user.get_verification()
    except Exception as exc:
        return send_error(exc.message)
    data = {
        'username': request.user.username,
        'token': token,
    }
    send_mail_template('verification', [request.user.email], data=data)
    return send_success()


@app.route('/auth/verification/<token>')
def verify(token):
    if User.verify_email(token):
        return send_success()
    return send_error('token not found')


@app.route('/auth/login', methods=['POST'])
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


@app.route('/auth/logout')
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
