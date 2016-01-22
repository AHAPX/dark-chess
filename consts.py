UNKNOWN = 0

# kinds of figures
PAWN = 1
ROOK = 2
KNIGHT = 3
BISHOP = 4
QUEEN = 5
KING = 6

FIGURES = {
    PAWN: 'pawn',
    ROOK: 'rook',
    KNIGHT: 'knight',
    BISHOP: 'bishop',
    QUEEN: 'queen',
    KING: 'king',
}

# colors of figures
WHITE = 1
BLACK = 2

COLORS = {
    WHITE: 'white',
    BLACK: 'black',
}

# moves of figures
BISHOP_MOVES = (1, 1), (-1, -1), (1, -1), (-1, 1)
KNIGHT_MOVES = (1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)
ROOK_MOVES = (1, 0), (-1, 0), (0, 1), (0, -1)
QUEEN_MOVES = BISHOP_MOVES + ROOK_MOVES
KING_MOVES = QUEEN_MOVES
