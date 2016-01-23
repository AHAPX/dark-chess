class BaseException(Exception):
    message = 'dark chess base exception'


class OutOfBoardError(BaseException):
    message = 'coordinates are out of board'


class CellIsBusyError(BaseException):
    message = 'you cannot cut your figure'


class WrongMoveError(BaseException):
    message = 'wrong move'


class WrongFigureError(BaseException):
    message = 'you can move only your figures'


class WrongTurnError(BaseException):
    message = 'it is not your turn'


class NotFoundError(BaseException):
    message = 'figure not found'


class EndGame(BaseException):
    message = 'game is over'


class WhiteWon(EndGame):
    message = 'white player won'


class BlackWon(EndGame):
    message = 'black player won'


class Draw(EndGame):
    message = 'draw'


class GameNotFoundError(BaseException):
    message = 'game not found'
