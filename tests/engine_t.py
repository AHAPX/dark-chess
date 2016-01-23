import unittest

import errors
from consts import WHITE, BLACK, PAWN, ROOK, KNIGHT, BISHOP, QUEEN, KING
from helpers import coors2pos
from engine import Figure, Pawn, Rook, Knight, Bishop, Queen, King, Board, Game


class TestFigure(unittest.TestCase):

    def test_symbol(self):
        self.assertEqual(str(Figure(1, 1, WHITE, None)), '?a1')
        self.assertEqual(str(Figure(1, 1, BLACK, None)), '?a1')

    def test_moves(self):
        figure = Figure(1, 1, WHITE, None)
        with self.assertRaises(NotImplementedError):
            figure.getMoves()
        with self.assertRaises(NotImplementedError):
            figure.update()
        figure._moves = [(5, 5)]
        self.assertEqual(figure.getMoves(), [(5, 5)])
        figure.reset()
        with self.assertRaises(NotImplementedError):
            figure.update()

    def test_friend_or_enemy(self):
        figure = Figure(1, 1, WHITE, None)
        self.assertTrue(figure.isFriend(Figure(2, 2, WHITE, None)))
        self.assertFalse(figure.isFriend(Figure(2, 2, BLACK, None)))

    def test_getLineMoves(self):
        board = Board()
        figure = Figure(5, 5, WHITE, board)
        self.assertEqual(figure.getLineMoves([(0, 0)]), [])
        self.assertEqual(figure.getLineMoves([(0, 1)]), [(5, 6), (5, 7)])
        self.assertEqual(figure.getLineMoves([(0, -1)]), [(5, 4), (5, 3)])

    def test_make_move(self):
        board = Board()
        figure = board.getFigure(WHITE, PAWN, 0)
        self.assertFalse(figure.moved)
        with self.assertRaises(errors.WrongMoveError):
            figure.move(2, 3)
        figure.move(1, 3)
        self.assertTrue(figure.moved)

    def test_terminate(self):
        board = Board()
        figure = board.getFigure(WHITE, PAWN, 0)
        self.assertEqual(len(board._figures[WHITE][PAWN]), 8)
        figure.terminate()
        self.assertEqual(len(board._figures[WHITE][PAWN]), 7)


class TestFigures(unittest.TestCase):

    def check_cases(self, color, kind, cases):
        for (board, results) in cases:
            figure = Board(board).getFigure(color, kind)
            self.assertEqual(sorted(figure.getMoves()), sorted(map(coors2pos, results)))

    def test_Pawn(self):
        self.assertEqual(str(Pawn(1, 1, WHITE, None)), 'Pa1')
        self.assertEqual(str(Pawn(1, 1, BLACK, None)), 'pa1')
        cases = [
            ('Pe2', ['e3', 'e4']),
            ('Pe3', ['e4']),
            ('Pe7', ['e8']),
            ('Pe2,Be4', ['e3']),
            ('Pe2,Be3', []),
            ('Pe4,pf5', ['e5', 'f5']),
            ('Pe4,pd5,pe5,pf5', ['d5', 'f5']),
        ]
        self.check_cases(WHITE, PAWN, cases)

    def test_Bishop(self):
        self.assertEqual(str(Bishop(1, 1, WHITE, None)), 'Ba1')
        self.assertEqual(str(Bishop(1, 1, BLACK, None)), 'ba1')
        cases = [
            ('Bd4', ['c3', 'b2', 'a1', 'c5', 'b6', 'a7', 'e3', 'f2', 'g1', 'e5', 'f6', 'g7', 'h8']),
            ('Bd4,pb6,pe5,Ra1', ['e5', 'c3', 'b2', 'e3', 'f2', 'g1', 'c5', 'b6']),
        ]
        self.check_cases(WHITE, BISHOP, cases)

    def test_Knight(self):
        self.assertEqual(str(Knight(1, 1, WHITE, None)), 'Na1')
        self.assertEqual(str(Knight(1, 1, BLACK, None)), 'na1')
        cases = [
            ('Ne4', ['d6', 'f6', 'g5', 'g3', 'f2', 'd2', 'c3', 'c5']),
            ('Ng4,Pe3,Rg2,pf6,rh6', ['f6', 'h6', 'h2', 'f2', 'e5']),
        ]
        self.check_cases(WHITE, KNIGHT, cases)

    def test_Rook(self):
        self.assertEqual(str(Rook(1, 1, WHITE, None)), 'Ra1')
        self.assertEqual(str(Rook(1, 1, BLACK, None)), 'ra1')
        cases = [
            ('Re4', ['e1', 'e2', 'e3', 'e5', 'e6', 'e7', 'e8', 'a4', 'b4', 'c4', 'd4', 'f4', 'g4', 'h4']),
            ('Re4,Bc4,Ke1,pe6,bf4', ['e3', 'e2', 'e5', 'e6', 'd4', 'f4']),
        ]
        self.check_cases(WHITE, ROOK, cases)

    def test_Queen(self):
        self.assertEqual(str(Queen(1, 1, WHITE, None)), 'Qa1')
        self.assertEqual(str(Queen(1, 1, BLACK, None)), 'qa1')
        cases = [
            (
                'Qd4', [
                    'c3', 'b2', 'a1', 'c5', 'b6', 'a7', 'e3', 'f2', 'g1', 'e5',
                    'f6', 'g7', 'h8', 'd1', 'd2', 'd3', 'd5', 'd6', 'd7', 'd8',
                    'a4', 'b4', 'c4', 'e4', 'f4', 'g4', 'h4'
                ]
            ),
            (
                'Qd4,Nb4,Nd2,Ra1,Bf2,qd5,pc5,pe4,nf6', [
                    'c3', 'b2', 'c5', 'e3', 'e5', 'f6', 'd3', 'd5', 'c4', 'e4'
                ]
            ),
        ]
        self.check_cases(WHITE, QUEEN, cases)







