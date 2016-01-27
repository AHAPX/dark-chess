from unittest.mock import patch
from datetime import datetime

from tests import TestCaseDB
import consts
from decorators import authenticated, with_game, formatted
from cache import set_cache, redis
from models import User, Game


class TestDecorators(TestCaseDB):

    @patch('decorators.request')
    def test_authenticated(self, request):
        func = authenticated(lambda *a, **k: 'success')
        request.json.get.return_value = '1234'
        # test decorator, token is not in cache
        with patch('decorators.send_error') as mock:
            mock.return_value = '_error'
            self.assertEqual(func(), '_error')
            mock.assert_called_once_with('not authorized')
        # test decorator, token is in cache, no user
        set_cache('1234', 1)
        with patch('decorators.send_error') as mock:
            mock.return_value = '_error'
            self.assertEqual(func(), '_error')
            mock.assert_called_once_with('not authorized')
        # test decorator success
        user = User.create(username='user1', password='passwd')
        set_cache('1234', user.pk)
        self.assertEqual(func(), 'success')
        self.assertEqual(request.user.pk, user.pk)
        self.assertEqual(request.auth, '1234')

    def test_with_game(self):
        func = with_game(lambda *a, **k: (a, k))
        # test decorator, tokens are not in cache
        with patch('decorators.send_error') as mock:
            mock.return_value = '_error'
            self.assertEqual(func('1234'), '_error')
            mock.assert_called_once_with('game not found')
        # test decorator, tokens are in cache
        game = Game.create()
        set_cache('1234', (game.pk, consts.WHITE, 'qwer'))
        set_cache('qwer', (game.pk, consts.BLACK, '1234'))
        self.assertEqual(func('1234')[0][0].model.pk, game.pk)
        self.assertEqual(func('qwer')[0][0].model.pk, game.pk)

    def test_formatted(self):
        func = formatted(lambda a: a)
        cases = [(
            {
                'k1': 123.546,
                'k2': datetime(2015, 1, 27, 12, 0, 4, 654),
                'k3': 'test',
            }, {
                'k1': 123.5,
                'k2': '2015-01-27 12:00:04',
                'k3': 'test',
            }
        ), (
            [123.554, datetime(2015, 1, 27, 12, 0, 4, 123), 'test'],
            [123.6, '2015-01-27 12:00:04', 'test'],
        ), (
            (123.554, datetime(2015, 1, 27, 12, 0, 4, 123), 'test'),
            (123.6, '2015-01-27 12:00:04', 'test'),
        )]
        for data, expect in cases:
            self.assertEqual(func(data), expect)
