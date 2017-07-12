from flask import request

from cache import (
    add_to_queue, get_from_queue, get_from_any_queue, set_cache, get_cache,
    delete_cache
)
import config
import consts
from connections import send_ws
from consts import WS_CHAT_MESSAGE
from decorators import validate
import errors
from game import Game
from handlers.v2.base import RestBase
from helpers import generate_token, get_prefix
from models import User, GamePool
from loggers import logger
from validators import GameNewValidator, GameMoveValidator


class RestGameBase(RestBase):
    pre_methods = ['load_game']

    def load_game(self, token):
        try:
            game = Game.load_game(token)
        except errors.GameNotStartedError as e:
            data = {
                'type': consts.TYPES[e.type]['name'],
                'limit': e.limit,
            }
            if (e.token):
                data['invite'] = e.token
            return data
        except errors.GameNotFoundError as e:
            raise errors.APIException(e.message)
        if game._loaded_by == consts.WHITE:
            if game.model.player_white is not None and game.model.player_white != request.user:
                raise errors.APIException('wrong user')
        else:
            if game.model.player_black is not None and game.model.player_black != request.user:
                raise errors.APIException('wrong user')
        self.game = game


class RestTypes(RestBase):
    def get(self):
        types = [{
            'name': t['name'],
            'description': t['description'],
            'periods': [{
                'name': k,
                'title': v[0],
            } for k, v in sorted(t['periods'].items(), key=lambda a: a[1][1])],
        } for t in consts.TYPES.values() if t['name'] != 'no limit']
        return {'types': types}


class RestNewGame(RestBase):
    def get(self):
        result = []
        count = 0
        for pool in GamePool.select().where(
            GamePool.is_started == False,
            GamePool.is_lost == False,
            GamePool.player1 is not None,
        ).order_by(GamePool.date_created.desc()):
            if pool.user1 and pool.user1 == request.user:
                continue
            result.append({
                'id': pool.pk,
                'date_created': pool.date_created.isoformat(),
                'user': pool.user1.username if pool.user1 else None,
                'type': consts.TYPES[pool.type_game]['name'],
                'limit': pool.time_limit,
            })
            count += 1
            if count > 9:
                break
        return {'games': result}

    @validate(GameNewValidator)
    def post(self):
        game_type = self.data['type']
        game_limit = self.data['limit']
        token = generate_token(True)
        pool = GamePool.create(
            player1 = token,
            user1 = request.user,
            type_game = game_type,
            time_limit = game_limit,
        )
        set_cache('wait_{}'.format(token), (game_type, game_limit))
        return {'game': token}


class RestAcceptGame(RestBase):
    def post(self, game_id):
        try:
            pool = GamePool.get(GamePool.pk == game_id)
        except GamePool.DoesNotExist:
            raise errors.APINotFound('game')
        except Exception as e:
            raise errors.APIException('wrong format')
        if pool.user1 and pool.user1 == request.user:
            raise errors.APIException('you cannot start game with yourself')
        pool.player2 = generate_token(True)
        pool.user2 = request.user
        pool.is_started = True
        pool.save()
        game = Game.new_game(
            pool.player1, pool.player2, pool.type_game, pool.time_limit,
            white_user=pool.user1, black_user=pool.user2
        )
        delete_cache('wait_{}'.format(pool.player1))
        result = {'game': pool.player2}
        result.update(game.get_info(consts.BLACK))
        return result


class RestNewInvite(RestBase):
    @validate(GameNewValidator)
    def post(self):
        game_type = self.data['type']
        game_limit = self.data['limit']
        if game_type != consts.TYPE_NOLIMIT and not game_limit:
            raise errors.APIException('game limit must be set for no limit game')
        token_game = generate_token(True)
        token_invite = generate_token(True)
        set_cache('invite_{}'.format(token_invite), (token_game, game_type, game_limit))
        if request.user:
            set_cache('user_{}'.format(token_game), request.user.pk, 3600)
        set_cache('wait_{}'.format(token_game), (game_type, game_limit, token_invite))
        return {
            'game': token_game,
            'invite': token_invite,
        }


class RestAcceptInvite(RestBase):
    def get(self, token):
        try:
            enemy_token, game_type, game_limit = get_cache('invite_{}'.format(token))
        except:
            raise errors.APINotFound('game')
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
        return result


class RestGames(RestBase):
    def get(self):
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
        return result


class RestInfo(RestGameBase):
    def get(self, *args, **kwargs):
        return self.game.get_info()


class RestMoves(RestGameBase):
    def get(self, *args, **kwargs):
        return self.game.moves()

    @validate(GameMoveValidator)
    def post(self, *args, **kwargs):
        coor1 = self.data['coor1']
        coor2 = self.data['coor2']
        return self.game.move(coor1, coor2)


class RestDraw(RestGameBase):
    # TODO: add get

    def post(self, *args, **kwargs):
        return self.game.draw_accept()

    def delete(self, *args, **kwargs):
        return self.game.draw_refuse()


class RestResign(RestGameBase):
    def post(self, *args, **kwargs):
        return self.game.resign()
