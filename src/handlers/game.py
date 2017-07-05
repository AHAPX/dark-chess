from flask import request, Blueprint

import consts
from serializers import send_data, send_error
from decorators import with_game, use_cache, authenticated, validated
from cache import (
    add_to_queue, get_from_queue, get_from_any_queue, set_cache, get_cache,
    delete_cache
)
from helpers import generate_token, get_prefix
from game import Game
from models import User, GamePool
from validators import GameNewValidator, GameMoveValidator
import errors


bp = Blueprint('game', __name__, url_prefix='/v1/game')


@bp.route('/types')
@use_cache()
def types():
    types = [{
        'name': t['name'],
        'description': t['description'],
        'periods': [{
            'name': k,
            'title': v[0],
        } for k, v in sorted(t['periods'].items(), key=lambda a: a[1][1])],
    } for t in consts.TYPES.values() if t['name'] != 'no limit']
    return send_data({'types': types})


@bp.route('/new', methods=['GET', 'POST'])
@authenticated
def new():

    @validated(GameNewValidator)
    def _post(data):
        game_type = data['type']
        game_limit = data['limit']
        token = generate_token(True)
        pool = GamePool.create(
            player1 = token,
            user1 = request.user,
            type_game = game_type,
            time_limit = game_limit,
        )
        set_cache('wait_{}'.format(token), (game_type, game_limit))
        return send_data({'game': token})

    if request.method == 'GET':
        result = []
        for pool in GamePool.select().where(
            GamePool.is_started == False,
            GamePool.is_lost == False,
            GamePool.player1 is not None
        ):
            result.append({
                'id': pool.pk,
                'date_created': pool.date_created.isoformat(),
                'user': pool.user1.username if pool.user1 else None,
                'type': consts.TYPES[pool.type_game]['name'],
                'limit': consts.PERIODS.get(pool.time_limit),
            })
        return send_data({'games': result})
    elif request.method == 'POST':
        return _post()

@bp.route('/invite', methods=['POST'])
@authenticated
@validated(GameNewValidator)
def invite(data):
    game_type = data['type']
    game_limit = data['limit']
    if game_type != consts.TYPE_NOLIMIT and not game_limit:
        return send_error('game limit must be set for no limit game')
    token_game = generate_token(True)
    token_invite = generate_token(True)
    set_cache('invite_{}'.format(token_invite), (token_game, game_type, game_limit))
    if request.user:
        set_cache('user_{}'.format(token_game), request.user.pk, 3600)
    set_cache('wait_{}'.format(token_game), (game_type, game_limit, token_invite))
    return send_data({
        'game': token_game,
        'invite': token_invite,
    })


@bp.route('/invite/<token>')
@authenticated
def invited(token):
    try:
        enemy_token, game_type, game_limit = get_cache('invite_{}'.format(token))
    except:
        return send_error('game not found')
    enemy_user = None
    user_id = get_cache('user_{}'.format(enemy_token))
    if user_id:
        try:
            enemy_user = User.get(pk=user_id)
        except User.DoesNotExist:
# TODO: if user not found game will be created with None as white player
            pass
    user_token = generate_token(True)
    game = Game.new_game(
        enemy_token, user_token, game_type, game_limit,
        white_user=enemy_user, black_user=request.user
    )
    delete_cache('wait_{}'.format(enemy_token))
    result = {'game': user_token}
    result.update(game.get_info(consts.BLACK))
    return send_data(result)


@bp.route('/games')
@authenticated
def games():
    from models import Game

    result = {
        'games': {
            'actives': [],
            'ended': [],
        }
    }
    if request.user:
        games = Game.select().where(
            Game.date_end == None,
            (Game.player_white == request.user) | (Game.player_black == request.user),
        )
        for game in games:
            if game.player_white == request.user:
                result['games']['actives'].append(game.white)
            else:
                result['games']['actives'].append(game.black)
        games = Game.select().where(
            Game.date_end != None,
            (Game.player_white == request.user) | (Game.player_black == request.user),
        ).limit(10)
        for game in games:
            if game.player_white == request.user:
                result['games']['ended'].append(game.white)
            else:
                result['games']['ended'].append(game.black)
    return send_data(result)


@bp.route('/<token>/info')
@use_cache(1, name='game_info_handler')
@authenticated
@with_game
def info(game):
    return send_data(game.get_info())


@bp.route('/<token>/move', methods=['POST'])
@authenticated
@with_game
@validated(GameMoveValidator)
def move(game, data):
    coor1 = data['coor1']
    coor2 = data['coor2']
    return game.move(coor1, coor2)


@bp.route('/<token>/draw/accept')
@authenticated
@with_game
def draw_accept(game):
    return game.draw_accept()


@bp.route('/<token>/draw/refuse')
@authenticated
@with_game
def draw_refuse(game):
    return game.draw_refuse()


@bp.route('/<token>/resign')
@authenticated
@with_game
def resign(game):
    return game.resign()


@bp.route('/<token>/moves')
@use_cache(name='game_moves_handler')
@authenticated
@with_game
def moves(game):
    return game.moves()
