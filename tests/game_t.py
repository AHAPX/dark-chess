import unittest
from unittest.mock import patch, call
from datetime import datetime

from tests.base import TestCaseDB
from consts import (
    WHITE, BLACK, TYPE_NOLIMIT, KING,
    WS_START, WS_MOVE, WS_DRAW, WS_LOSE, WS_WIN, WS_DRAW_REQUEST,
    END_DRAW, END_RESIGN, END_CHECKMATE
)
from game import Game
from cache import get_cache, set_cache
import models
import errors
from format import format


class TestGameInit(TestCaseDB):

    @patch('game.Game.get_info')
    def test_new_game(self, get_info):
        get_info.return_value = 'info'
        with patch('game.Game.send_ws') as mock:
            game = Game.new_game('1234', 'qwer', TYPE_NOLIMIT, None)
            self.assertIsInstance(game, Game)
            self.assertEqual(get_cache('1234'), (game.model.pk, WHITE, 'qwer'))
            self.assertEqual(get_cache('qwer'), (game.model.pk, BLACK, '1234'))
            mock.assert_has_calls([
                call('info', WS_START, WHITE), call('info', WS_START, BLACK)
            ])

    @patch('game.Game.get_info')
    def test_load_game(self, get_info):
        get_info.return_value = 'info'
        # game is not existed
        with self.assertRaises(errors.GameNotFoundError):
            Game.load_game('1234')
        # create game
        model = models.Game.create()
        set_cache('1234', (model.pk, WHITE, 'qwer'))
        set_cache('qwer', (model.pk, BLACK, '1234'))
        # load game for white player and check
        game = Game.load_game('1234')
        self.assertEqual(game.model.pk, model.pk)
        # load game for black player with time end
        with patch('models.Game.is_time_over') as mock,\
                patch('game.Game.send_ws') as mock1:
            mock.return_value = True
            game = Game.load_game('qwer')
            mock1.assert_has_calls([
                call('info', WS_LOSE, BLACK),
                call('info', WS_WIN, WHITE)
            ])


class TestGame(TestCaseDB):

    def setUp(self):
        super(TestGame, self).__init__()
        model = models.Game.create()
        set_cache('1234', (model.pk, WHITE, 'qwer'))
        set_cache('qwer', (model.pk, BLACK, '1234'))
        self.game = Game.load_game('1234')

    def test_get_color(self):
        # try get color without _loaded_by
        game = Game('1234', 'qwer')
        self.assertEqual(game.get_color(WHITE), WHITE)
        self.assertEqual(game.get_color(BLACK), BLACK)
        with self.assertRaises(ValueError):
            game.get_color()
        # try get color with _loaded_by
        self.assertEqual(Game.load_game('1234').get_color(), WHITE)
        self.assertEqual(Game.load_game('qwer').get_color(), BLACK)

    @patch('game.BoardSerializer')
    def test_get_board(self, BoardSerializer):
        self.game.get_board()
        BoardSerializer.assert_called_once_with(self.game.game.board, WHITE)

    @patch('game.Game.time_left')
    @patch('game.Game.get_board')
    def test_get_info_1(self, get_board, time_left):
        get_board.return_value = 'board'
        time_left.return_value = 12.567
        expect = {
            'board': 'board',
            'time_left': 12.6,
            'enemy_time_left': 12.6,
            'started_at': format(self.game.model.date_created),
            'ended_at': None,
            'next_turn': 'white',
            'color': 'white',
            'opponent': 'anonymous',
        }
        self.assertEqual(self.game.get_info(), expect)
        get_board.assert_called_once_with(WHITE)
        time_left.assert_has_calls([call(WHITE), call(BLACK)])

    @patch('game.BoardSerializer.calc')
    def test_get_info_2(self, board_calc):
        self.game.model.game_over(END_CHECKMATE, winner=WHITE)
        board_calc.return_value = 'board'
        expect = {
            'board': 'board',
            'started_at': format(self.game.model.date_created),
            'ended_at': format(self.game.model.date_end),
            'color': 'white',
            'opponent': 'anonymous',
            'winner': 'white',
        }
        self.assertEqual(self.game.get_info(), expect)
        board_calc.assert_called_once_with()

    def test_time_left(self):
        with patch('models.Game.time_left') as mock:
            self.game.time_left()
            mock.assert_called_once_with(WHITE)

    def test_send_ws(self):
        # without color
        with patch('game.send_ws') as mock:
            self.game.send_ws('msg', 'sig')
            mock.assert_called_once_with('msg', 'sig', ['qwer', '1234'])
        # with white color
        with patch('game.send_ws') as mock:
            self.game.send_ws('msg', 'sig', WHITE)
            mock.assert_called_once_with('msg', 'sig', ['1234'])
        # with black color
        with patch('game.send_ws') as mock:
            self.game.send_ws('msg', 'sig', BLACK)
            mock.assert_called_once_with('msg', 'sig', ['qwer'])

    @patch('game.Game.get_info')
    def test_draw_accept(self, get_info):
        get_info.return_value = 'info'
        # add draw request
        with patch('game.send_success') as mock, patch('game.Game.send_ws') as mock1:
            self.game.draw_accept()
            mock.assert_called_once_with()
            mock1.assert_called_once_with('opponent offered draw', WS_DRAW_REQUEST, BLACK)
        # add draw accept, game should be over
        with patch('game.send_data') as mock,\
                patch('game.send_ws') as mock1:
            self.game.draw_accept(BLACK)
            mock.assert_called_once_with('info')
        # game is over
        with patch('game.send_error') as mock:
            self.game.model.date_end = datetime.now()
            self.game.draw_accept()
            mock.assert_called_once_with('game is over')

    def test_draw_refuse_1(self):
        # add draw request and check cache
        with patch('game.send_success') as mock,\
                patch('game.Game.send_ws') as mock1:
            self.game.draw_accept()
            mock.assert_called_once_with()
            mock1.assert_called_once_with('opponent offered draw', WS_DRAW_REQUEST, BLACK)
        self.assertFalse(get_cache(self.game._get_draw_name(BLACK)))
        self.assertTrue(get_cache(self.game._get_draw_name(WHITE)))
        # delete draw by white and check cache again
        with patch('game.send_success') as mock:
            self.game.draw_refuse()
            mock.assert_called_once_with()
        self.assertFalse(get_cache(self.game._get_draw_name(BLACK)))
        self.assertFalse(get_cache(self.game._get_draw_name(WHITE)))

    def test_draw_refuse_2(self):
        # add draw request and check cache
        with patch('game.send_success') as mock,\
                patch('game.Game.send_ws') as mock1:
            self.game.draw_accept(WHITE)
            mock.assert_called_once_with()
            mock1.assert_called_once_with('opponent offered draw', WS_DRAW_REQUEST, BLACK)
        self.assertFalse(get_cache(self.game._get_draw_name(BLACK)))
        self.assertTrue(get_cache(self.game._get_draw_name(WHITE)))
        # refuse draw by black and check cache again
        with patch('game.send_success') as mock:
            self.game.draw_refuse(BLACK)
            mock.assert_called_once_with()
        self.assertFalse(get_cache(self.game._get_draw_name(BLACK)))
        self.assertFalse(get_cache(self.game._get_draw_name(WHITE)))

    def test_draw_refuse_3(self):
        # try to refuse ended game
        with patch('game.send_error') as mock:
            self.game.model.date_end = datetime.now()
            self.game.draw_refuse()
            mock.assert_called_once_with('game is over')

    @patch('game.Game.get_info')
    @patch('game.Game.send_ws')
    def test_check_draw(self, send_ws, get_info):
        get_info.return_value = 'info'
        # check draw without draw request
        self.assertFalse(self.game.check_draw())
        # added draw requests without checking draw inside
        with patch('game.send_success'), patch('game.Game.check_draw') as mock:
            mock.return_value = False
            self.game.draw_accept(WHITE)
            self.game.draw_accept(BLACK)
        # check draw successful
        self.assertTrue(self.game.check_draw())
        self.assertEqual(self.game.model.end_reason, END_DRAW)
        send_ws.assert_has_calls([
            call('info', WS_DRAW, WHITE),
            call('info', WS_DRAW, BLACK)
        ])
        # check draw when game is over
        self.assertFalse(self.game.check_draw())

    @patch('game.Game.get_info')
    @patch('game.Game.send_ws')
    def test_resign(self, send_ws, get_info):
        get_info.return_value = 'info'
        # resign game successfully
        with patch('game.send_data') as mock:
            self.game.resign()
            self.assertEqual(self.game.model.end_reason, END_RESIGN)
            mock.assert_called_once_with('info')
            send_ws.assert_called_once_with('info', WS_WIN, BLACK)
        send_ws.reset_mock()
        # try to resign when game is over
        with patch('game.send_error') as mock:
            self.game.resign()
            mock.assert_called_once_with('game is over')
            self.assertFalse(send_ws.called)

    @patch('game.Game.get_info')
    @patch('game.Game.onMove')
    @patch('game.Game.send_ws')
    def test_move(self, send_ws, onMove, get_info):
        # make move successful
        get_info.return_value = {'_name': 'info'}
        with patch('game.send_data') as mock,\
                patch('game.Game.get_board') as mock1:
            mock1.return_value = 'board'
            self.game.move('e2', 'e4')
            self.assertEqual(mock.call_count, 1)
            expect = {
                '_name': 'info',
                'number': 1,
            }
            onMove.assert_called_once_with()
            send_ws.assert_called_once_with(expect, WS_MOVE, BLACK)
        send_ws.reset_mock()
        onMove.reset_mock()
        # wrong turn
        with patch('game.send_error') as mock:
            self.game.move('e7', 'e5')
            mock.assert_called_once_with(errors.WrongTurnError.message)
            self.assertFalse(onMove.called)
            self.assertFalse(send_ws.called)
        # wrong color of figure
        with patch('game.send_error') as mock:
            self.game.move('e4', 'e5', BLACK)
            mock.assert_called_once_with(errors.WrongFigureError.message)
        # not found figure
        with patch('game.send_error') as mock:
            self.game.move('e6', 'e5', BLACK)
            mock.assert_called_once_with(errors.NotFoundError.message)
        # wrong move
        with patch('game.send_error') as mock:
            self.game.move('e7', 'd7', BLACK)
            mock.assert_called_once_with(errors.WrongMoveError.message)
        # wrong cell
        with patch('game.send_error') as mock:
            self.game.move('e9', 'e8', BLACK)
            mock.assert_called_once_with(errors.OutOfBoardError.message)
        # db error
        with patch('game.send_error') as mock, patch('models.Game.add_move') as mock1:
            mock1.side_effect = Exception('db error')
            with self.assertLogs('game', level='ERROR'):
                self.game.move('e7', 'e5', BLACK)
            mock.assert_called_once_with('system error')
        self.assertFalse(onMove.called)
        self.assertFalse(send_ws.called)
        # move with ending game
        with patch('game.send_data') as mock, patch('engine.Game.move') as mock1:
            error = errors.BlackWon()
            error.reason = END_CHECKMATE
            error.figure = self.game.game.board.getFigure(BLACK, KING)
            error.move = 'e7-e5'
            mock1.side_effect = error
            self.game.move('e7', 'e5', BLACK)
            mock.assert_called_once_with({'_name': 'info', 'number': 2})
            send_ws.assert_has_calls([
                call({'number': 2, '_name': 'info'}, WS_LOSE, WHITE),
            ])
            onMove.assert_called_once_with()

    @patch('game.get_cache_func_name')
    @patch('game.delete_cache')
    def test_onMove(self, delete_cache, get_cache_func_name):
        self.game.onMove()
        get_cache_func_name.assert_has_calls([
            call('game_info_handler', token=self.game.white),
            call('game_info_handler', token=self.game.black),
            call('game_moves_handler', token=self.game.white),
            call('game_moves_handler', token=self.game.black),
        ])
        self.assertEqual(delete_cache.call_count, 4)

    @patch('game.Game.get_info')
    def test_moves(self, get_info):
        get_info.return_value = {'_name': 'info'}
        with patch('game.send_data') as mock,\
                patch('game.send_ws') as mock1:
            self.game.move('e2', 'e4', WHITE)
            self.game.move('e7', 'e5', BLACK)
            self.game.move('b2', 'b3', WHITE)
            self.game.move('d7', 'd6', BLACK)
            mock.reset_mock()
            mock1.reset_mock()
            # only white moves
            expect = {'moves': ['e2-e4', 'b2-b3']}
            Game.load_game('1234').moves()
            mock.assert_called_once_with(expect)
            mock.reset_mock()
            # only black moves
            expect = {'moves': ['e7-e5', 'd7-d6']}
            Game.load_game('qwer').moves()
            mock.assert_called_once_with(expect)
            mock.reset_mock()
            # all moves
            self.game.model.game_over(END_DRAW)
            expect = {'moves': ['e2-e4', 'e7-e5', 'b2-b3', 'd7-d6']}
            Game.load_game('1234').moves()
            Game.load_game('qwer').moves()
            mock.assert_has_calls([call(expect), call(expect)])
