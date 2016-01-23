import logging
import pickle

import engine
import models
import consts
import errors
from serializers import GameSerializer, BoardSerializer, send_error
from helpers import coors2pos
from cache import set_cache, get_cache


logger = logging.getLogger(__name__)


class Game(object):

    def __init__(self, white_token, black_token):
        self.white = white_token
        self.black = black_token
        self._loaded_by = None

    @classmethod
    def new_game(cls, white_token, black_token, white_user=None, black_user=None):
        game = cls(white_token, black_token)
        game.game = engine.Game()
        game.model = models.Game.create(
            player_white=white_user,
            player_black=black_user,
            state=str(game.game.board),
        )
        set_cache(white_token, pickle.dumps((game.model.pk, consts.WHITE, black_token)))
        set_cache(black_token, pickle.dumps((game.model.pk, consts.BLACK, white_token)))
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
        return BoardSerializer(self.game.board, self.get_color(color)).to_json()

    def move(self, coor1, coor2, color=None):
        try:
            color = self.get_color(color)
            figure, move = self.game.move(color, coors2pos(coor1), coors2pos(coor2))
        except errors.WrongTurnError:
            return send_error('it is not your turn')
        except errors.NotFoundError:
            return send_error('figure not found')
        except errors.WrongFigureError:
            return send_error('you can move only your figures')
        except errors.OutOfBoardError:
            return send_error('coordinates are out of board')
        except errors.WrongMoveError, errors.CellIsBusyError:
            return send_error('wrong move')
        else:
            try:
                self.model.add_move(figure.symbol, move)
                self.model.save_state(str(self.game.board), self.game.current_player)
            except Exception as exc:
                logger.error(exc)
                return send_error('system error')
            return GameSerializer(self.game, color).to_json()
