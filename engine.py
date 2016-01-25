from helpers import onBoard, invertColor, pos2coors, coors2pos
from errors import (
    OutOfBoardError, CellIsBusyError, EndGame, WhiteWon, BlackWon, Draw,
    WrongMoveError, NotFoundError, WrongTurnError, WrongFigureError
)
from consts import *


class Board(object):
    _figures = {}
    _figure_list = []
    _moves = []

    def __init__(self, figures=None):
        if figures is not None:
            self.loadFigures(figures)
        else:
            self.standFigures()
        self.updateFigures()

    def standFigures(self):
        self._figures = {
            WHITE: {
                PAWN: [Pawn(x, 2, WHITE, self) for x in range(1, 9)],
                ROOK: [Rook(x, 1, WHITE, self) for x in (1, 8)],
                KNIGHT: [Knight(x, 1, WHITE, self) for x in (2, 7)],
                BISHOP: [Bishop(x, 1, WHITE, self) for x in (3, 6)],
                QUEEN: [Queen(4, 1, WHITE, self)],
                KING: King(5, 1, WHITE, self)
            },
            BLACK: {
                PAWN: [Pawn(x, 7, BLACK, self) for x in range(1, 9)],
                ROOK: [Rook(x, 8, BLACK, self) for x in (1, 8)],
                KNIGHT: [Knight(x, 8, BLACK, self) for x in (2, 7)],
                BISHOP: [Bishop(x, 8, BLACK, self) for x in (3, 6)],
                QUEEN: [Queen(4, 8, BLACK, self)],
                KING: King(5, 8, BLACK, self)
            }
        }
        self._figure_list = []
        for color in (WHITE, BLACK):
            for figs in self._figures.get(color).values():
                if (isinstance(figs, list)):
                    for fig in figs:
                        self._figure_list.append(fig)
                else:
                    self._figure_list.append(figs)

    def loadFigures(self, line):
        figures = {
            WHITE: {PAWN: [], ROOK: [], KNIGHT: [], BISHOP: [], QUEEN: [], KING: None},
            BLACK: {PAWN: [], ROOK: [], KNIGHT: [], BISHOP: [], QUEEN: [], KING: None}
        }
        figure_list = []
        for fig in line.split(','):
            cls, color = FIGURES_MAP[fig[0]]
            x, y = coors2pos(fig[1:3])
            figure = cls(x, y, color, self)
            if cls == King:
                figures[color][cls.kind] = figure
            else:
                figures[color][cls.kind].append(figure)
            figure_list.append(figure)
        self._figures = figures
        self._figure_list = figure_list

    def cell2Figure(self, x, y):
        if not onBoard(x, y):
            raise OutOfBoardError
        for fig in self.figures:
            if fig.x == x and fig.y == y:
                return fig

    def isProtected(self, x, y, color):
        if not onBoard(x, y):
            raise OutOfBoardError
        for fig in self.figures:
            if fig.color != color:
                continue
            if isinstance(fig, King):
                moves = fig.royalAura()
            else:
                moves = fig.getMoves()
            if (x, y) in moves:
                return True
        return False

    def move(self, figure, x, y):
        end_game = None
        fig = self.cell2Figure(x, y)
        if fig:
            if fig.color == figure.color:
                raise CellIsBusyError
            else:
                if isinstance(fig, King):
                    if fig.color == WHITE:
                        end_game = BlackWon
                    else:
                        end_game = WhiteWon
                self._figure_list.remove(fig)
                fig.terminate()
        self._moves.append({
            'figure': figure,
            'x1': figure.x,
            'y1': figure.y,
            'x2': x,
            'y2': y,
        })
        figure.x, figure.y = x, y
        self.updateFigures()
        if end_game:
            raise end_game
        for fig in self.figures:
            if fig.color == figure.color:
                continue
            if len(fig.getMoves()):
                return
        raise Draw

    def __str__(self):
        return ','.join(map(str, self.figures))

    def updateFigures(self):
        for fig in self.figures:
            fig.reset()
        for fig in self.figures:
            fig.update()

    @property
    def figures(self):
        return self._figure_list

    def getFigure(self, color, kind, index=0):
        try:
            figs = self._figures[color][kind]
            if not figs:
                raise NotFoundError
            if isinstance(figs, list):
                return figs[index]
            return figs
        except:
            raise NotFoundError

    def castle(self, king, rook):
        if rook.x == 8:
            king.x, rook.x = 7, 6
        else:
            king.x, rook.x = 3, 4
        self.updateFigures()

    @property
    def moves(self):
        return self._moves


class Figure(object):

    color = UNKNOWN
    kind = UNKNOWN
    x, y = 0, 0
    _symbol = '?'
    _moves = None
    _moved = False

    def __init__(self, x, y, color, board):
        self.x = x
        self.y = y
        self.color = color
        self.board = board

    @property
    def symbol(self):
        if self.color == WHITE:
            return self._symbol.upper()
        return self._symbol.lower()

    def __str__(self):
        return '{}{}'.format(self.symbol, pos2coors(self.x, self.y))

    def getMoves(self):
        if self._moves is None:
            self.updateMoves()
        return self._moves

    def updateMoves(self):
        raise NotImplementedError

    def move(self, x, y):
        if (x, y) not in self.getMoves():
            raise WrongMoveError
        self.board.move(self, x, y)
        self._moved = True

    def isEnemy(self, figure):
        return figure.color != self.color

    def isFriend(self, figure):
        return figure.color == self.color

    def getLineMoves(self, deltaList):
        moves = []
        for dx, dy in deltaList:
            if dx == 0 and dy == 0:
                continue
            x, y = self.x, self.y
            while True:
                x += dx
                y += dy
                try:
                    fig = self.board.cell2Figure(x, y)
                except OutOfBoardError:
                    break
                if fig:
                    if self.isEnemy(fig):
                        moves.append((x, y))
                    break
                moves.append((x, y))
        return moves

    def update(self):
        self.updateMoves()

    def reset(self):
        _moves = None

    @property
    def moved(self):
        return self._moved

    def terminate(self):
        self.board._figures[self.color][self.kind].remove(self)

    def getVisibleCells(self):
        return self.getMoves()


class Pawn(Figure):
    _symbol = 'P'
    kind = PAWN

    def updateMoves(self):
        result, moves = [], []
        if self.color == WHITE:
            if self.y == 2:
                moves += [(self.x, 3), (self.x, 4)]
            elif self.y < 8:
                moves.append((self.x, self.y + 1))
            cutMoves = (self.x - 1, self.y + 1), (self.x + 1, self.y + 1)
        else:
            if self.y == 7:
                moves += [(self.x, 6), (self.x, 5)]
            elif self.y > 1:
                moves.append((self.x, self.y - 1))
            cutMoves = (self.x - 1, self.y - 1), (self.x + 1, self.y - 1)
        for x, y in moves:
            try:
                fig = self.board.cell2Figure(x, y)
            except OutOfBoardError:
                break
            if fig:
                break
            result.append((x, y))
        for x, y in cutMoves:
            try:
                fig = self.board.cell2Figure(x, y)
            except OutOfBoardError:
                continue
            if fig and self.isEnemy(fig):
                result.append((x, y))
        self._moves = result

    def getVisibleCells(self):
        cells = []
        if self.color == WHITE:
            if self.y == 2:
                cells.append((self.x, 3))
                if not self.board.cell2Figure(self.x, 3):
                    cells.append((self.x, 4))
            elif self.y < 8:
                cells.append((self.x, self.y + 1))
            cells += [(self.x - 1, self.y + 1), (self.x + 1, self.y + 1)]
        else:
            if self.y == 7:
                cells.append((self.x, 6))
                if not self.board.cell2Figure(self.x, 6):
                    cells.append((self.x, 5))
            elif self.y > 1:
                cells.append((self.x, self.y - 1))
            cells += [(self.x - 1, self.y - 1), (self.x + 1, self.y - 1)]
        return cells


class Bishop(Figure):
    _symbol = 'B'
    kind = BISHOP

    def updateMoves(self):
        self._moves = self.getLineMoves(BISHOP_MOVES)


class Knight(Figure):
    _symbol = 'N'
    kind = KNIGHT

    def updateMoves(self):
        moves = []
        for dx, dy in (KNIGHT_MOVES):
            x = self.x + dx
            y = self.y + dy
            try:
                fig = self.board.cell2Figure(x, y)
            except OutOfBoardError:
                continue
            if not fig or self.isEnemy(fig):
                moves.append((x, y))
        self._moves = moves


class Rook(Figure):
    _symbol = 'R'
    kind = ROOK

    def updateMoves(self):
        self._moves = self.getLineMoves(ROOK_MOVES)


class Queen(Figure):
    _symbol = 'Q'
    kind = QUEEN

    def updateMoves(self):
        self._moves = self.getLineMoves(QUEEN_MOVES)


class King(Figure):
    _symbol = 'K'
    _aura = []
    kind = KING

    def updateMoves(self):
        moves = []
        for dx, dy in KING_MOVES:
            x = self.x + dx
            y = self.y + dy
            try:
                fig = self.board.cell2Figure(x, y)
            except OutOfBoardError:
                continue
            if not fig or self.isEnemy(fig):
                moves.append((x, y))
        self._moves = moves

    def updateAura(self):
        aura = []
        for dx, dy in KING_MOVES:
            x = self.x + dx
            y = self.y + dy
            if onBoard(x, y):
                aura.append((x, y))
        self._aura = aura

    def royalAura(self):
        if self._aura is None:
            self.updateAura()
        return self._aura

    def update(self):
        super(King, self).update()
        self.updateAura()

    def reset(self):
        super(King, self).reset()
        self._aura = None

    def can_castle(self, short=True):
        if self.moved:
            return False
        if self.color == WHITE:
            y = 1
        else:
            y = 8
        if short:
            rook_x = 8
            cells = ((6, y), (7, y))
        else:
            rook_x = 1
            cells = ((2, y), (3, y), (4, y))
        try:
            rook = self.board.cell2Figure(x=rook_x, y=y)
            if not rook or rook.moved:
                return False
        except (NotFoundError, OutOfBoardError):
            return False
        for cell in cells:
            try:
                if self.board.cell2Figure(*cell):
                    return False
            except OutOfBoardError:
                return False
        return rook

    def castle(self, short=True):
        rook = self.can_castle(short)
        if not rook:
            raise WrongMoveError
        self.board.castle(self, rook)

    def try_to_castle(self, x, y):
        if (self.color == WHITE and (x, y) in ((7, 1), (3, 1))) or \
           (self.color == BLACK and (x, y) in ((7, 8), (3, 8))):
            try:
                self.castle(x == 7)
                move = '0-0' if x == 7 else '0-0-0'
            except WrongMoveError:
                pass
            except EndGame as exc:
                exc.move = move
                raise exc
            else:
                return move
        return False

    def remove(self, *args, **kwargs):
        del self

    def getVisibleCells(self):
        return self.royalAura()


class Game(object):

    def __init__(self, figures=None, current_player=WHITE):
        self.board = Board(figures)
        self.current_player = current_player

    def move(self, color, pos1, pos2):
        if color != self.current_player:
            raise WrongTurnError
        figure = self.board.cell2Figure(*pos1)
        if not figure:
            raise NotFoundError
        if figure.color != color:
            raise WrongFigureError
        try:
            castled = isinstance(figure, King) and figure.try_to_castle(*pos2)
        except EndGame as exc:
            exc.figure = figure
            raise exc
        if not castled:
            result = figure, '{}-{}'.format(pos2coors(*pos1), pos2coors(*pos2))
            try:
                figure.move(*pos2)
            except EndGame as exc:
                exc.figure, exc.move = result
                raise exc
        else:
            result = figure, castled
        self.current_player = invertColor(self.current_player)
        return result

    @property
    def moves(self):
        return self.board.moves


FIGURES_MAP = {
    'p': (Pawn, BLACK),
    'r': (Rook, BLACK),
    'n': (Knight, BLACK),
    'b': (Bishop, BLACK),
    'q': (Queen, BLACK),
    'k': (King, BLACK),
    'P': (Pawn, WHITE),
    'R': (Rook, WHITE),
    'N': (Knight, WHITE),
    'B': (Bishop, WHITE),
    'Q': (Queen, WHITE),
    'K': (King, WHITE),
}
