from flask import request, Blueprint

import consts
from serializers import send_data, send_error
from decorators import with_game, use_cache, authenticated, validated
from cache import add_to_queue, get_from_queue, get_from_any_queue, set_cache, get_cache
from helpers import generate_token, get_prefix
from game import Game
from models import User
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
    } for t in consts.TYPES.values()]
    return send_data({'types': types})


@bp.route('/new', methods=['POST'])
@authenticated
@validated(GameNewValidator)
def new(data):
    game_type = data['type']
    game_limit = data['limit']
    queue_prefix = get_prefix(game_type, game_limit)
    if game_type == consts.TYPE_NOLIMIT or game_limit:
        enemy_token = get_from_queue(queue_prefix)
        if not enemy_token:
            enemy_token = get_from_queue(get_prefix(game_type))
    else:
        enemy_token, game_limit = get_from_any_queue(game_type)
    token = generate_token(True)
    result = {'game': token}
    if enemy_token:
        enemy_user = None
        user_id = get_cache('user_{}'.format(enemy_token))
        if user_id:
            try:
                enemy_user = User.get(pk=user_id)
            except User.DoesNotExist:
                pass
            else:
                if enemy_user == request.user:
                    add_to_queue(token, queue_prefix)
                    return send_data(result)
        game = Game.new_game(
            enemy_token, token, game_type, game_limit,
            white_user=enemy_user, black_user=request.user
        )
        result.update(game.get_info(consts.BLACK))
    else:
        add_to_queue(token, queue_prefix)
        if request.user:
            set_cache('user_{}'.format(token), request.user.pk, 3600)
    return send_data(result)


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
            pass
    user_token = generate_token(True)
    game = Game.new_game(
        enemy_token, user_token, game_type, game_limit,
        white_user=enemy_user, black_user=request.user
    )
    result = {'game': user_token}
    result.update(game.get_info(consts.BLACK))
    return send_data(result)


@bp.route('/active')
@authenticated
def active():
    from models import Game

    result = {'games': []}
    if request.user:
        games = Game.select().where(
            Game.date_end == None,
            (Game.player_white == request.user) | (Game.player_black == request.user),
        )
        for game in games:
            try:
                white_token, black_token = get_cache('game_{}'.format(game.pk))
            except:
                pass
            else:
                if game.player_white == request.user:
                    result['games'].append(white_token)
                else:
                    result['games'].append(black_token)
    return send_data(result)


@bp.route('/<token>/info')
@use_cache(1, name='game_info_handler')
@with_game
def info(game):
    return send_data(game.get_info())


@bp.route('/<token>/move', methods=['POST'])
@with_game
@validated(GameMoveValidator)
def move(game, data):
    coor1 = data['coor1']
    coor2 = data['coor2']
    return game.move(coor1, coor2)


@bp.route('/<token>/draw/accept')
@with_game
def draw_accept(game):
    return game.draw_accept()


@bp.route('/<token>/draw/refuse')
@with_game
def draw_refuse(game):
    return game.draw_refuse()


@bp.route('/<token>/resign')
@with_game
def resign(game):
    return game.resign()


@bp.route('/<token>/moves')
@use_cache(name='game_moves_handler')
@with_game
def moves(game):
    return game.moves()
