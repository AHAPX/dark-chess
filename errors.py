class OutOfBoardError(Exception): pass

class CellIsBusyError(Exception): pass

class WrongMoveError(Exception): pass

class WrongFigureError(Exception): pass

class WrongTurnError(Exception): pass

class NotFoundError(Exception): pass

class EndGame(Exception): pass

class WhiteWon(EndGame): pass

class BlackWon(EndGame): pass

class Draw(EndGame): pass
