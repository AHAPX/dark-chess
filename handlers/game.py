from flask import request

import consts
from serializers import send_data, send_error
from decorators import with_game, use_cache
from cache import add_to_queue, get_from_queue, get_from_any_queue
from helpers import generate_token, get_prefix
from game import Game
from app import app


@app.route('/game/types')
@use_cache()
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


@app.route('/game/<token>/info')
@use_cache(1, name='game_info_handler')
@with_game
def _game_info(game):
    return send_data(game.get_info())


@app.route('/game/<token>/move/<move>')
@with_game
def _game_move(game, move):
    moves = move.split('-')
    if len(moves) == 2:
        return game.move(*moves)
    return send_error('move format must be like e2-e4')


@app.route('/game/<token>/draw/accept')
@with_game
def _draw_accept(game):
    return game.draw_accept()


@app.route('/game/<token>/draw/refuse')
@with_game
def _draw_refuce(game):
    return game.draw_refuse()


@app.route('/game/<token>/resign')
@with_game
def _resign(game):
    return game.resign()


@app.route('/game/<token>/moves')
@use_cache(name='game_moves_handler')
@with_game
def _moves(game):
    return game.moves()
