import logging
import pickle

import engine
import models
import consts
import errors
from serializers import BoardSerializer, send_error, send_message, send_success
from helpers import coors2pos, invert_color
from cache import set_cache, get_cache
from connections import send_ws


logger = logging.getLogger(__name__)


class Game(object):

    def __init__(self, white_token, black_token):
        self.white = white_token
        self.black = black_token
        self._loaded_by = None

    @classmethod
    def new_game(cls, white_token, black_token, type_game, time_limit, white_user=None, black_user=None):
        game = cls(white_token, black_token)
        game.game = engine.Game()
        game.model = models.Game.create(
            player_white=white_user,
            player_black=black_user,
            state=str(game.game.board),
            type_game=type_game,
            time_limit=time_limit,
        )
        set_cache(white_token, pickle.dumps((game.model.pk, consts.WHITE, black_token)))
        set_cache(black_token, pickle.dumps((game.model.pk, consts.BLACK, white_token)))
        game.send_ws(game.get_board(consts.WHITE), consts.WS_START, consts.WHITE)
        game.send_ws(game.get_board(consts.BLACK), consts.WS_START, consts.BLACK)
        return game

    @classmethod
    def load_game(cls, token):
        try:
            game_id, color, enemy_token = pickle.loads(get_cache(token))
            if color == consts.WHITE:
                wt, bt = token, enemy_token
            elif color == consts.BLACK:
                wt, bt = enemy_token, token
            game = cls(wt, bt)
            game.model = models.Game.get(pk=game_id)
            game.game = engine.Game(game.model.state, game.model.next_color)
            game._loaded_by = color
            if game.model.is_time_over():
                game.send_ws('you lose by time', consts.WS_LOSE, color)
                game.send_ws('you win by time', consts.WS_WIN, invert_color(color))
        except:
            raise errors.GameNotFoundError
        return game

    def get_color(self, color=None):
        if color is None:
            color = self._loaded_by
        if color not in (consts.WHITE, consts.BLACK):
            raise ValueError('color is not declared')
        return color

    def get_board(self, color=None):
        return BoardSerializer(self.game.board, self.get_color(color)).calc()

    def get_info(self, color=None):
        color = self.get_color(color)
        return {
            'board': self.get_board(color),
            'time_left': self.time_left(color),
            'enemy_time_left': self.time_left(invert_color(color)),
        }

    def time_left(self, color=None):
        return round(self.model.time_left(self.get_color(color)), 1)

    def move(self, coor1, coor2, color=None):
        if self.model.ended:
            return send_error('game is over')
        game_over = None
        try:
            color = self.get_color(color)
            figure, move = self.game.move(color, coors2pos(coor1), coors2pos(coor2))
        except errors.EndGame as exc:
            game_over, figure, move = exc.message, exc.figure, exc.move
        except errors.BaseException as exc:
            return send_error(exc.message)
        try:
            num = self.model.add_move(
                figure.symbol, move, str(self.game.board), game_over
            ).number
        except Exception as exc:
            logger.error(exc)
            return send_error('system error')
        if game_over:
            self.send_ws('you lose', consts.WS_LOSE, invert_color(color))
            return send_message(game_over)
        msg = {
            'number': num,
            'move': move,
            'board': self.get_board(invert_color(color)),
            'time_left': self.time_left(invert_color(color)),
            'enemy_time_left': self.time_left(color),
        }
        self.send_ws(msg, consts.WS_MOVE, invert_color(color))
        return send_success()

    def send_ws(self, msg, signal, color=consts.UNKNOWN):
        tags = []
        if color != consts.WHITE:
            tags.append(self.black)
        if color != consts.BLACK:
            tags.append(self.white)
        send_ws(msg, signal, tags)
