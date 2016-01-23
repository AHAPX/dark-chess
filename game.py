import logging

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
            if color == WHITE:
                wt, bt = token, enemy_token
            else:
                wt, bt = enemy_token, token
            game = cls(wt, bt)
            game.model = models.Game.get(pk=game_id)
            game.game = engine.Game(game.model.state)
        except:
            raise error.GameNotFoundError
        return game

    def get_board(self, color):
        return BoardSerializer(self.game.board, color).to_json()

    def move(self, color, coor1, coor2):
        try:
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
                self.model.save_state(str(self.game.board))
            except Exception as exc:
                logger.error(exc)
                return send_error('system error')
            return GameSerializer(self.game, color).to_json()
