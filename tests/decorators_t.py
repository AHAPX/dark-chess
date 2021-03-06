from unittest.mock import patch, MagicMock
from datetime import datetime

from tests.base import TestCaseDB
import consts
from decorators import (authenticated, with_game, formatted, use_cache,
    login_required, validated)
from cache import set_cache, delete_cache, get_cache_func_name
from models import User, Game
from helpers import invert_color
import errors


class TestDecorators(TestCaseDB):

    @patch('decorators.request')
    def test_authenticated(self, request):
        func = authenticated(lambda *a, **k: 'success')
        request.json.get.return_value = '1234'
        # test decorator, token is not in cache
        self.assertEqual(func(), 'success')
        self.assertIsNone(request.user)
        self.assertIsNone(request.auth)
        # test decorator, token is in cache, no user
        set_cache('1234', 1)
        self.assertEqual(func(), 'success')
        self.assertIsNone(request.user)
        self.assertIsNone(request.auth)
        # test decorator success
        user = User.create(username='user1', password='passwd')
        set_cache('1234', user.pk)
        self.assertEqual(func(), 'success')
        self.assertEqual(request.user.pk, user.pk)
        self.assertEqual(request.auth, '1234')

    @patch('decorators.request')
    def test_login_required(self, request):
        request.user = None
        func = login_required(lambda *a, **k: 'success')
        with patch('decorators.send_error') as mock:
            mock.return_value = '_error'
            self.assertEqual(func(), '_error')
            mock.assert_called_once_with('not authorized')
        request.user = User.create(username='user1', password='passwd')
        self.assertEqual(func(), 'success')

    def test_with_game_1(self):
        func = with_game(lambda *a, **k: (a, k))
        # test decorator, tokens are not in cache
        with patch('decorators.send_error') as mock:
            mock.return_value = '_error'
            self.assertEqual(func('1234'), '_error')
            mock.assert_called_once_with('game not found')
        # test decorator, tokens are in cache
        game = Game.create(white='1234', black='qwer')
        self.assertEqual(func('1234')[0][0].model.pk, game.pk)
        self.assertEqual(func('qwer')[0][0].model.pk, game.pk)
        # waited game
        set_cache('wait_5678', (consts.TYPE_FAST, 3600))
        with patch('decorators.send_data') as mock:
            func('5678')
            mock.assert_called_once_with({'type': 'fast', 'limit': 3600})
        # invited game
        set_cache('wait_asdf', (consts.TYPE_FAST, 3600, 'zxcv'))
        with patch('decorators.send_data') as mock:
            func('asdf')
            mock.assert_called_once_with({'type': 'fast', 'limit': 3600, 'invite': 'zxcv'})

    @patch('decorators.request')
    def test_with_game_2(self, request):
        request.json.get.return_value = 'user_token'
        # create game with white user and try to get it anonymously
        func = authenticated(with_game(lambda *a, **k: (a, k)))
        user = User.create(username='user1', password='passwd')
        game = Game.create(white='1234', black='qwer', player_white=user)
        with patch('decorators.send_error') as mock:
            func('1234')
            mock.assert_called_once_with('wrong user')
        self.assertEqual(func('qwer')[0][0].model.pk, game.pk)
        # set auth and check again
        set_cache('user_token', user.pk)
        self.assertEqual(func('1234')[0][0].model.pk, game.pk)

    def test_formatted(self):
        func = formatted(lambda a: a)
        # cases for dict, list and tuple
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

    def test_use_cache(self):
        def _func(a, b):
            invert_color(a)
            return 'ok'

        func = use_cache(10, name='test_func')(_func)
        a, b = Game.create(white='1234', black='qwer'), delete_cache
        # run first time, no cache
        with patch('tests.decorators_t.invert_color') as mock:
            self.assertEqual(func(a, b=b), 'ok')
            mock.assert_called_once_with(a)
        # run second time, results from cached
        with patch('tests.decorators_t.invert_color') as mock:
            self.assertEqual(func(a, b=b), 'ok')
            self.assertFalse(mock.called)
        # delete cache and run again, no cache
        delete_cache(get_cache_func_name('test_func', a, b=b))
        with patch('tests.decorators_t.invert_color') as mock:
            self.assertEqual(func(a, b=b), 'ok')
            mock.assert_called_once_with(a)

    def test_validated(self):
        dummy_validator = MagicMock()
        func = validated(dummy_validator)(lambda *a, **k: 'ok')
        self.assertEqual(func(), 'ok')
        # raise error
        dummy_validator.side_effect = errors.ValidationError('a')
        with patch('decorators.send_error') as mock:
            mock.return_value = '_error'
            self.assertEqual(func(), '_error')
            mock.assert_called_once_with('a is not valid')
