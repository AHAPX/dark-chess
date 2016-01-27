import config
from tests.base import TestCaseBase
from helpers import (
    onBoard, pos2coors, coors2pos, invert_color, encrypt_password, generate_token,
    with_context, get_queue_name, get_prefix
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
        self.assertTrue(len(generate_token()) > 10)

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
