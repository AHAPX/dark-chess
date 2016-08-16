import unittest

import errors
from tests.base import TestCaseBase
from consts import WHITE, BLACK, PAWN, ROOK, KNIGHT, BISHOP, QUEEN, KING
from helpers import coors2pos
from engine import Figure, Pawn, Rook, Knight, Bishop, Queen, King, Board, Game


class TestFigure(TestCaseBase):

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


class TestFiguresMoves(TestCaseBase):

    def check_cases(self, color, kind, cases):
        for (board, results) in cases:
            figure = Board(board).getFigure(color, kind)
            self.assertEqual(sorted(figure.getMoves()), sorted(map(coors2pos, results)))

    def check_cases_visible(self, color, kind, cases):
        for (board, results) in cases:
            figure = Board(board).getFigure(color, kind)
            self.assertEqual(sorted(figure.getVisibleCells()), sorted(map(coors2pos, results)))

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
        cases_vis = [
            ('Pe2', ['e3', 'e4', 'd3', 'f3']),
            ('Pe2,qe3', ['e3', 'd3', 'f3']),
        ]
        self.check_cases(WHITE, PAWN, cases)
        self.check_cases_visible(WHITE, PAWN, cases_vis)

    def test_Bishop(self):
        self.assertEqual(str(Bishop(1, 1, WHITE, None)), 'Ba1')
        self.assertEqual(str(Bishop(1, 1, BLACK, None)), 'ba1')
        cases = [
            ('Bd4', ['c3', 'b2', 'a1', 'c5', 'b6', 'a7', 'e3', 'f2', 'g1', 'e5', 'f6', 'g7', 'h8']),
            ('Bd4,pb6,pe5,Ra1', ['e5', 'c3', 'b2', 'e3', 'f2', 'g1', 'c5', 'b6']),
        ]
        self.check_cases(WHITE, BISHOP, cases)
        self.check_cases_visible(WHITE, BISHOP, cases)

    def test_Knight(self):
        self.assertEqual(str(Knight(1, 1, WHITE, None)), 'Na1')
        self.assertEqual(str(Knight(1, 1, BLACK, None)), 'na1')
        cases = [
            ('Ne4', ['d6', 'f6', 'g5', 'g3', 'f2', 'd2', 'c3', 'c5']),
            ('Ng4,Pe3,Rg2,pf6,rh6', ['f6', 'h6', 'h2', 'f2', 'e5']),
        ]
        self.check_cases(WHITE, KNIGHT, cases)
        self.check_cases_visible(WHITE, KNIGHT, cases)

    def test_Rook(self):
        self.assertEqual(str(Rook(1, 1, WHITE, None)), 'Ra1')
        self.assertEqual(str(Rook(1, 1, BLACK, None)), 'ra1')
        cases = [
            ('Re4', ['e1', 'e2', 'e3', 'e5', 'e6', 'e7', 'e8', 'a4', 'b4', 'c4', 'd4', 'f4', 'g4', 'h4']),
            ('Re4,Bc4,Ke1,pe6,bf4', ['e3', 'e2', 'e5', 'e6', 'd4', 'f4']),
        ]
        self.check_cases(WHITE, ROOK, cases)
        self.check_cases_visible(WHITE, ROOK, cases)

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
        self.check_cases_visible(WHITE, QUEEN, cases)

    def test_King(self):
        self.assertEqual(str(King(1, 1, WHITE, None)), 'Ka1')
        self.assertEqual(str(King(1, 1, BLACK, None)), 'ka1')
        cases = [
            ('Ke4', ['d5', 'e5', 'f5', 'f4', 'f3', 'e3', 'd3', 'd4']),
            ('Ke4,Pd3,Rg2,nd5,re6', ['d5', 'e5', 'f5', 'f4', 'f3', 'e3', 'd4']),
            ('Ke1,Ra1,Rh1', ['c1', 'd1', 'd2', 'e2', 'f2', 'f1', 'g1']),
            ('Ke1,Ra1,Rh1,nb1', ['d1', 'd2', 'e2', 'f2', 'f1', 'g1']),
        ]
        self.check_cases(WHITE, KING, cases)


class TestKing(TestCaseBase):

    # aura isn't required
    @unittest.skip
    def test_aura(self):
        results = ['d5', 'e5', 'f5', 'f4', 'f3', 'e3', 'd3', 'd4']
        king = Board('Ke4,Pd3,Rf3,nd5,re6').getFigure(WHITE, KING)
        self.assertEqual(sorted(king.royalAura()), sorted(map(coors2pos, results)))

    def test_can_castle_1(self):
        # check for white after move
        king = Board('Kd1,Rh1,ke8').getFigure(WHITE, KING)
        king.move(5, 1)
        self.assertFalse(king.can_castle())
        king = Board('Ke1,Rh2,ke8').getFigure(WHITE, KING)
        king.board.getFigure(WHITE, ROOK).move(8, 1)
        self.assertFalse(king.can_castle())
        # short castle
        king = Board('Ke1,Rh1,ke8').getFigure(WHITE, KING)
        self.assertIsInstance(king.can_castle(), Rook)
        self.assertFalse(king.can_castle(False))
        # short castle with barrier
        king = Board('Ke1,Rh1,Bf1,ke8').getFigure(WHITE, KING)
        self.assertFalse(king.can_castle())
        # long castle
        king = Board('Ke1,Ra1,ke8').getFigure(WHITE, KING)
        self.assertIsInstance(king.can_castle(False), Rook)
        self.assertFalse(king.can_castle())
        # long castle with barrier
        king = Board('Ke1,Ra1,Bc1,ke8').getFigure(WHITE, KING)
        self.assertFalse(king.can_castle(False))

    def test_can_castle_2(self):
        # check for black after move
        king = Board('Ke1,rh8,kd8').getFigure(BLACK, KING)
        king.move(5, 8)
        self.assertFalse(king.can_castle())
        king = Board('Ke1,rh7,ke8').getFigure(BLACK, KING)
        king.board.getFigure(BLACK, ROOK).move(8, 8)
        self.assertFalse(king.can_castle())
        # short castle
        king = Board('Ke1,rh8,ke8').getFigure(BLACK, KING)
        self.assertIsInstance(king.can_castle(), Rook)
        self.assertFalse(king.can_castle(False))
        # short castle with barrier
        king = Board('Ke1,rh8,bf8,ke8').getFigure(BLACK, KING)
        self.assertFalse(king.can_castle())
        # long castle
        king = Board('Ke1,ra8,ke8').getFigure(BLACK, KING)
        self.assertIsInstance(king.can_castle(False), Rook)
        self.assertFalse(king.can_castle())
        # long castle with barrier
        king = Board('Ke1,ra8,bc8,ke8').getFigure(BLACK, KING)
        self.assertFalse(king.can_castle(False))

    def test_can_castle_3(self):
        # white: deny castle separately and check it
        king = Board('Ke1,Rh1,Ra1,ke8').getFigure(WHITE, KING)
        self.assertTrue(king.can_castle(True))
        self.assertTrue(king.can_castle(False))
        king.board.denyCastle(WHITE, True)
        self.assertFalse(king.can_castle(True))
        self.assertTrue(king.can_castle(False))
        king.board.denyCastle(WHITE, False)
        self.assertFalse(king.can_castle(True))
        self.assertFalse(king.can_castle(False))
        # white: deny castle both and check it
        king = Board('Ke1,Rh1,Ra1,ke8').getFigure(WHITE, KING)
        self.assertTrue(king.can_castle(True))
        self.assertTrue(king.can_castle(False))
        king.board.denyCastle(WHITE)
        self.assertFalse(king.can_castle(True))
        self.assertFalse(king.can_castle(False))

    def test_can_castle_4(self):
        # black: deny castle separately and check it
        king = Board('Ke1,rh8,ra8,ke8').getFigure(BLACK, KING)
        self.assertTrue(king.can_castle(True))
        self.assertTrue(king.can_castle(False))
        king.board.denyCastle(BLACK, True)
        self.assertFalse(king.can_castle(True))
        self.assertTrue(king.can_castle(False))
        king.board.denyCastle(BLACK, False)
        self.assertFalse(king.can_castle(True))
        self.assertFalse(king.can_castle(False))
        # black: deny castle both and check it
        king = Board('Ke1,rh8,ra8,ke8').getFigure(BLACK, KING)
        self.assertTrue(king.can_castle(True))
        self.assertTrue(king.can_castle(False))
        king.board.denyCastle(BLACK)
        self.assertFalse(king.can_castle(True))
        self.assertFalse(king.can_castle(False))

    def test_castle_1(self):
        board = Board('Ke1,Rh1,ke8')
        king = board.getFigure(WHITE, KING)
        rook = board.getFigure(WHITE, ROOK)
        self.assertEqual(str(king), 'Ke1')
        self.assertEqual(str(rook), 'Rh1')
        king.castle()
        self.assertEqual(str(king), 'Kg1')
        self.assertEqual(str(rook), 'Rf1')

    def test_castle_2(self):
        board = Board('Ke1,Rh1,Ng1,ke8')
        king = board.getFigure(WHITE, KING)
        rook = board.getFigure(WHITE, ROOK)
        self.assertEqual(str(king), 'Ke1')
        self.assertEqual(str(rook), 'Rh1')
        with self.assertRaises(errors.WrongMoveError):
            king.castle()
        self.assertEqual(str(king), 'Ke1')
        self.assertEqual(str(rook), 'Rh1')

    def test_try_to_castle_white(self):
        # short castle
        king = Board('Ke1,Rh1,ke8').getFigure(WHITE, KING)
        self.assertFalse(king.try_to_castle(6, 1))
        self.assertFalse(king.try_to_castle(8, 1))
        self.assertEqual(king.try_to_castle(7, 1), '0-0')
        # long castle
        king = Board('Ke1,Ra1,ke8').getFigure(WHITE, KING)
        self.assertFalse(king.try_to_castle(1, 1))
        self.assertFalse(king.try_to_castle(2, 1))
        self.assertFalse(king.try_to_castle(4, 1))
        self.assertEqual(king.try_to_castle(3, 1), '0-0-0')

    def test_try_to_castle_black(self):
        # short castle
        king = Board('Ke1,rh8,ke8').getFigure(BLACK, KING)
        self.assertFalse(king.try_to_castle(6, 8))
        self.assertFalse(king.try_to_castle(8, 8))
        self.assertEqual(king.try_to_castle(7, 8), '0-0')
        # long castle
        king = Board('Ke1,ra8,ke8').getFigure(BLACK, KING)
        self.assertFalse(king.try_to_castle(1, 8))
        self.assertFalse(king.try_to_castle(2, 8))
        self.assertFalse(king.try_to_castle(4, 8))
        self.assertEqual(king.try_to_castle(3, 8), '0-0-0')


class TestGame(TestCaseBase):

    def test_move(self):
        game = Game('Kf3,Pe2,ke8,qf7')
        self.assertEqual(game.current_player, WHITE)
        with self.assertRaises(errors.WrongTurnError):
            game.move(BLACK, (5, 4), (5, 5))
        with self.assertRaises(errors.NotFoundError):
            game.move(WHITE, (5, 4), (5, 5))
        with self.assertRaises(errors.WrongFigureError):
            game.move(WHITE, (5, 8), (5, 7))
        with self.assertRaises(errors.WrongMoveError):
            game.move(WHITE, (5, 2), (5, 5))
        fig, move = game.move(WHITE, (5, 2), (5, 4))
        self.assertIsInstance(fig, Pawn)
        self.assertEqual(move, 'e2-e4')
        self.assertEqual(game.current_player, BLACK)
        with self.assertRaises(errors.BlackWon) as cm:
            game.move(BLACK, (6, 7), (6, 3))
        self.assertIsInstance(cm.exception.figure, Queen)
        self.assertEqual(cm.exception.move, 'f7-f3')
        game = Game('Ke1,Rh1,ke8')
        fig, move = game.move(WHITE, (5, 1), (7, 1))
        self.assertIsInstance(fig, King)
        self.assertEqual(move, '0-0')
        self.assertEqual(game.current_player, BLACK)

    def test_full_game(self):
        moves = [
            'e2-e4', 'e7-e5', 'g1-f3', 'b8-c6', 'f1-c4', 'c6-d4', 'f3-e5',
            'd8-g5', 'e5-f7', 'g5-g2', 'h1-f1', 'g2-e4', 'c4-e2', 'd4-f3',
            'e2-f3', 'e4-e1'
        ]
        game = Game()
        with self.assertRaises(errors.BlackWon):
            for move in moves:
                positions = map(coors2pos, move.split('-'))
                game.move(game.current_player, *positions)
        expect = [
            'Pa2', 'Pb2', 'Pc2', 'Pd2', 'Pf2', 'Ph2', 'Ra1', 'Rf1', 'Nb1', 'Nf7',
            'Bc1', 'Bf3', 'Qd1', 'pa7', 'pb7', 'pc7', 'pd7', 'pg7', 'ph7', 'ra8',
            'rh8', 'ng8', 'bc8', 'bf8', 'qe1', 'ke8'
        ]
        self.assertEqual(str(game.board), ','.join(expect))
