import config
from tests.base import TestCaseBase
from helpers import (
    onBoard, pos2coors, coors2pos, invert_color, encrypt_password, generate_token,
    with_context, get_queue_name, get_prefix, get_request_arg
)
from consts import WHITE, BLACK


class TestHelpers(TestCaseBase):

    def test_onBoard(self):
        self.assertTrue(onBoard(1, 1))
        self.assertTrue(onBoard(8, 8))
        self.assertFalse(onBoard(0, 1))
        self.assertFalse(onBoard(9, 1))
        self.assertFalse(onBoard(1, 0))
        self.assertFalse(onBoard(1, 9))

    def test_pos2coors(self):
        with self.assertRaises(TypeError):
            pos2coors('1', 1)
        with self.assertRaises(TypeError):
            pos2coors(1.0, 1)
        with self.assertRaises(ValueError):
            pos2coors(0, 1)
        self.assertEqual(pos2coors(1, 1), 'a1')
        self.assertEqual(pos2coors(8, 8), 'h8')

    def test_coors2pos(self):
        with self.assertRaises(ValueError):
            coors2pos('e')
        with self.assertRaises(ValueError):
            coors2pos('e12')
        with self.assertRaises(ValueError):
            coors2pos('ee')
        with self.assertRaises(ValueError):
            coors2pos('x1')
        self.assertEqual(coors2pos('a1'), (1, 1))
        self.assertEqual(coors2pos('h8'), (8, 8))

    def test_invert_color(self):
        self.assertEqual(invert_color(WHITE), BLACK)
        self.assertEqual(invert_color(BLACK), WHITE)

    def test_encrypt_password(self):
        config.PASSWORD_SALT = 'salt'
        self.assertEqual(encrypt_password('password'), 'd514dee5e76bbb718084294c835f312c')

    def test_generate_token(self):
        self.assertEqual(len(generate_token()), 32)
        self.assertEqual(len(generate_token(False)), 32)
        self.assertEqual(len(generate_token(True)), config.TOKEN_SHORT_LENGTH)
        tokens = []
        for i in range(1000):
            token = generate_token(True)
            self.assertNotIn(token, tokens)
            tokens.append(token)

    def test_with_context(self):
        expect = {
            'key': 'value',
            'site_url': config.SITE_URL,
        }
        self.assertEqual(with_context({'key': 'value'}), expect)

    def test_get_queue_name(self):
        self.assertEqual(get_queue_name('pref'), 'pref_{}'.format(config.GAME_QUEUE_NAME))

    def test_get_prefix(self):
        self.assertEqual(get_prefix(123), '123-*')
        self.assertEqual(get_prefix(123, 30), '123-30')

    def test_get_request_arg(self):
        class _Request():
            form = {}
            json = None
        # None value
        request = _Request()
        self.assertIsNone(get_request_arg(request, 'arg1'))
        # from json
        request.json = {'arg1': 'jsuccess'}
        self.assertEqual(get_request_arg(request, 'arg1'), 'jsuccess')
        # from form
        request.form['arg1'] = 'fsuccess'
        self.assertEqual(get_request_arg(request, 'arg1'), 'fsuccess')
