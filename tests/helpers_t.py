import unittest

import config
from helpers import onBoard, pos2coors, coors2pos, invertColor, encryptPassword, generateToken
from consts import WHITE, BLACK


class TestHelpers(unittest.TestCase):

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

    def test_invertColor(self):
        self.assertEqual(invertColor(WHITE), BLACK)
        self.assertEqual(invertColor(BLACK), WHITE)

    def test_encryptPassword(self):
        config.PASSWORD_SALT = 'salt'
        self.assertEqual(encryptPassword('password'), 'd514dee5e76bbb718084294c835f312c')

    def test_generateToken(self):
        self.assertTrue(len(generateToken()) > 10)
