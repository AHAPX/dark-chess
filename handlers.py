import datetime

from flask import request, make_response
from validate_email import validate_email

import config
import consts
from serializers import send_data, send_message, send_error, send_success
from decorators import authenticated, with_game
from models import User
from cache import delete_cache, add_to_queue, get_from_queue, get_from_any_queue
from helpers import generate_token, get_prefix
from app import app
from connections import send_mail_template
from game import Game


@app.route('/')
def _index():
    return send_message('welcome to dark chess')


@app.route('/auth/register', methods=['POST'])
def _register():
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
def _get_verification():
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
def _verify(token):
    if User.verify_email(token):
        return send_success()
    return send_error('token not found')


@app.route('/auth/login', methods=['POST'])
def _login():
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
def _logout():
    delete_cache(request.auth)
    response = make_response(send_message('logout successfully'))
    response.set_cookie('auth', expires=0)
    return response


@app.route('/game/types')
def _types():
    types = {
        t['name']: {
            'description': t['description'],
            'periods': t['periods']
        } for t in consts.TYPES.values()
    }
    return send_data({'types': types})


@app.route('/game/new')
def _new_game():
    _type = request.args.get('type', 'nolimit')
    _limit = request.args.get('limit')
    game_type = consts.TYPES_NAMES.get(_type)
    if game_type is None:
        return send_error('{} is not available type'.format(_type))
    if game_type != consts.TYPE_NOLIMIT and _limit:
        try:
            game_limit = consts.TYPES[game_type]['periods'][_limit][1]
        except:
            return send_error('{} limit is not available found for {} game'.format(_limit, _type))
    else:
        game_limit = None
    queue_prefix = get_prefix(game_type, game_limit)
    if game_type == consts.TYPE_NOLIMIT or game_limit:
        enemy_token = get_from_queue(queue_prefix)
        if not enemy_token:
            enemy_token = get_from_queue(get_prefix(game_type))
    else:
        enemy_token, game_limit = get_from_any_queue(game_type)
    token = generate_token()
    result = {'game': token}
    if enemy_token:
        game = Game.new_game(enemy_token, token, game_type, game_limit)
        result.update(game.get_info(consts.BLACK))
    add_to_queue(token, queue_prefix)
    return send_data(result)


@app.route('/game/info/<token>')
@with_game
def _game_info(game):
    return send_data(game.get_info())


@app.route('/game/move/<token>/<move>')
@with_game
def _game_move(game, move):
    moves = move.split('-')
    if len(moves) == 2:
        return game.move(*moves)
    return send_error('move format must be like e2-e4')
