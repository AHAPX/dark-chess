UNKNOWN = 0

# kinds of figures
PAWN    = 1
ROOK    = 2
KNIGHT  = 3
BISHOP  = 4
QUEEN   = 5
KING    = 6

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

# ws signals
WS_NONE  = 0x0000
WS_START = 0x0001
WS_MOVE  = 0x0002
WS_END   = 0x0010
WS_WIN   = 0x0011
WS_LOSE  = 0x0012
WS_DRAW  = 0x0013
WS_DRAW_REQUEST = 0x0021
WS_CHAT_MESSAGE = 0x0031

# types of games
TYPE_NOLIMIT = 1
TYPE_SLOW    = 2
TYPE_FAST    = 3

TYPES = {
    TYPE_NOLIMIT: {
        'name': 'no limit',
        'description': 'no time limits',
        'periods': {},
    },
    TYPE_SLOW: {
        'name': 'slow',
        'description': 'long game, time limit for each move, no limit for game',
        'periods': {
            '1d': ('1 day', 24 * 60 * 60),
            '3d': ('3 days', 3 * 24 * 60 * 60),
            '7d': ('7 days', 7 * 24 * 60 * 60),
            '15d': ('15 days', 15 * 24 * 60 * 60),
            '30d': ('30 days', 30 * 24 * 60 * 60),
        },
    },
    TYPE_FAST: {
        'name': 'fast',
        'description': 'short game, time limit for game, moves do not reset timer',
        'periods': {
            '5m': ('5 minutes', 5 * 60),
            '10m': ('10 minutes', 10 * 60),
            '30m': ('30 minutes', 30 * 60),
            '1h': ('1 hour', 60 * 60),
            '3h': ('3 hours', 3 * 60 * 60),
        },
    },
}

TYPES_NAMES = {value['name']: key for key, value in TYPES.items()}
PERIODS = {k: v for d in [{v[1]: k for k, v in x['periods'].items()} for x in TYPES.values()] for k, v in d.items()}

# end reasons
END_CHECKMATE = 1
END_DRAW = 2
END_RESIGN = 3
END_TIME = 4
