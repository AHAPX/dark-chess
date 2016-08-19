import logging

import engine
import models
import consts
import errors
from serializers import (
    BoardSerializer, MoveSerializer, send_error, send_success, send_data,
)
from helpers import coors2pos, invert_color
from cache import set_cache, get_cache, delete_cache, get_cache_func_name
from connections import send_ws
from decorators import formatted
from format import format


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
            white = white_token,
            black = black_token,
            player_white=white_user,
            player_black=black_user,
            state=str(game.game.board),
            type_game=type_game,
            time_limit=time_limit,
        )
        delete_cache('wait_{}'.format(white_token))
        delete_cache('wait_{}'.format(black_token))
        game.send_ws(game.get_info(consts.WHITE), consts.WS_START, consts.WHITE)
        game.send_ws(game.get_info(consts.BLACK), consts.WS_START, consts.BLACK)
        return game

    @classmethod
    def load_game(cls, token):
        try:
            try:
                game_model = models.Game.get_game(token)
            except models.Game.DoesNotExist:
                data = get_cache('wait_{}'.format(token))
                if data:
                    raise errors.GameNotStartedError(*data)
                raise errors.GameNotFoundError
            game = cls(game_model.white, game_model.black)
            game.model = game_model
            game.game = engine.Game(game.model.state, game.model.next_color, game.model.cut)
            game._loaded_by = game_model._loaded_by
            if game.model.is_time_over():
                winner = game.model.winner
                loser = invert_color(winner)
                game.send_ws(game.get_info(loser), consts.WS_LOSE, loser)
                game.send_ws(game.get_info(winner), consts.WS_WIN, winner)
            if not game.model.ended:
                game.check_draw()
                game.check_castles()
        except errors.GameNotStartedError:
            raise
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

    @formatted
    def get_info(self, color=None):
        color = self.get_color(color)
        if color == consts.WHITE:
            opponent = self.model.player_black
        else:
            opponent = self.model.player_white
        if self.model.ended:
            return {
                'board': BoardSerializer(self.game.board, consts.UNKNOWN).calc(),
                'started_at': self.model.date_created,
                'ended_at': self.model.date_end,
                'color': consts.COLORS[color],
                'opponent': opponent.username if opponent else 'anonymous',
                'winner': self.model.get_winner(),
            }
        return {
            'board': self.get_board(color),
            'time_left': self.time_left(color),
            'enemy_time_left': self.time_left(invert_color(color)),
            'started_at': self.model.date_created,
            'ended_at': self.model.date_end,
            'next_turn': consts.COLORS[self.game.current_player],
            'color': consts.COLORS[color],
            'opponent': opponent.username if opponent else 'anonymous',
        }

    def time_left(self, color=None):
        return self.model.time_left(self.get_color(color))

    def move(self, coor1, coor2, color=None):
        if self.model.ended:
            return send_error('game is over')
        game_over = None
        try:
            color = self.get_color(color)
            figure, move = self.game.move(color, coors2pos(coor1), coors2pos(coor2))
        except errors.EndGame as exc:
            game_over, figure, move = exc.reason, exc.figure, exc.move
        except errors.BaseException as exc:
            return send_error(exc.message)
        try:
            num = self.model.add_move(
                figure.symbol, move, str(self.game.board), game_over
            ).number
        except Exception as exc:
            logger.error(exc)
            return send_error('system error')
        if self.game.board._cut:
            self.model.cut += self.game.board._cut.symbol
            self.model.save()
        self.onMove()
        msg = self.get_info(invert_color(color))
        msg.update({'number': num})
        if game_over:
            self.send_ws(msg, consts.WS_LOSE, invert_color(color))
            return send_data(self.get_info())
        self.send_ws(msg, consts.WS_MOVE, invert_color(color))
        return send_data(self.get_info())

    def send_ws(self, msg, signal, color=consts.UNKNOWN):
        tags = []
        if color != consts.WHITE:
            tags.append(self.black)
        if color != consts.BLACK:
            tags.append(self.white)
        send_ws(msg, signal, tags)

    def _get_draw_name(self, color):
        return 'game-{}-draw-{}'.format(self.model.pk, color)

    def draw_accept(self, color=None):
        if self.model.ended:
            return send_error('game is over')
        color = self.get_color(color)
        set_cache(self._get_draw_name(color), True)
        if self.check_draw():
            return send_data(self.get_info())
        self.send_ws('opponent offered draw', consts.WS_DRAW_REQUEST, invert_color(color))
        return send_success()

    def draw_refuse(self, color=None):
        if self.model.ended:
            return send_error('game is over')
        color = self.get_color
        delete_cache(self._get_draw_name(color))
        delete_cache(self._get_draw_name(invert_color(color)))
        return send_success()

    def check_draw(self):
        if not self.model.ended:
            name1 = self._get_draw_name(consts.WHITE)
            name2 = self._get_draw_name(consts.BLACK)
            if get_cache(name1) and get_cache(name2):
                self.model.game_over(consts.END_DRAW)
                delete_cache(name1)
                delete_cache(name2)
                msg = self.get_info()
                self.send_ws(msg, consts.WS_DRAW, consts.WHITE)
                self.send_ws(msg, consts.WS_DRAW, consts.BLACK)
                self.onMove()
                return True
        return False

    def resign(self, color=None):
        if self.model.ended:
            return send_error('game is over')
        winner = invert_color(self.get_color(color))
        self.model.game_over(consts.END_RESIGN, winner=winner)
        self.send_ws(self.get_info(winner), consts.WS_WIN, winner)
        self.onMove()
        return send_data(self.get_info())

    def moves(self, color=None):
        if not self.model.ended:
            color = self.get_color(color)
        else:
            color = None
        return send_data({
            'moves': [MoveSerializer(m).calc() for m in self.model.get_moves(color)]
        })

    def onMove(self):
        for name in ('game_info_handler', 'game_moves_handler'):
            delete_cache(get_cache_func_name(name, token=self.white))
            delete_cache(get_cache_func_name(name, token=self.black))

    def check_castles(self, color=None, log=False):
        color = self.get_color(color)
        if color == consts.WHITE:
            king = 'K'
            y = 1
        else:
            king = 'k'
            y = 8
        if self.model.moves.where(models.Move.figure == king).count():
            self.game.board.denyCastle(color)
        else:
            if self.model.moves.where(models.Move.color == color,
                    models.Move.move.startswith('a{}'.format(y))).count():
                self.game.board.denyCastle(color, False)
            if self.model.moves.where(models.Move.color == color,
                    models.Move.move.startswith('h{}'.format(y))).count():
                self.game.board.denyCastle(color, True)
