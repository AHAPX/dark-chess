class BaseException(Exception):
    message = 'dark chess base exception'


class BaseArgException(BaseException):
    def __init__(self, *args, **kwargs):
        self.message = self.message.format(*args, **kwargs)
        super(BaseArgException, self).__init__(*args, **kwargs)


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


class TooOftenRequestError(BaseArgException):
    message = 'too often requests, try again after {} seconds'

    def __init__(self, seconds):
        super(TooOftenRequestError, self).__init__(seconds)


class VerifiedError(BaseException):
    message = 'your email is already verified'


class VerificationRequestError(TooOftenRequestError):
    message = 'you must wait {} seconds to get new verification code'
