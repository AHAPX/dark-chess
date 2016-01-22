import engine
import models
from serializers import GameSerializer, BoardSerializer, send_error
from helpers import coors2pos
import errors


class Game(object):

    def __init__(self, white_token, black_token, white_user=None, black_user=None):
        self.white = white_token
        self.black = black_token
        self.model = models.Game.create(player_white=white_user, player_black=black_user)
        self.game = engine.Game()

    def get_board(self, color):
        return BoardSerializer(self.game.board, color).to_json()

    def move(self, color, coor1, coor2):
        try:
            self.game.move(color, coors2pos(coor1), coors2pos(coor2))
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
            return GameSerializer(self.game, color).to_json()
