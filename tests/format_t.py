from datetime import datetime

from tests.base import TestCaseBase
from format import format, get_argument


class TestFormat(TestCaseBase):

    def test_format_1(self):
        # test simple formats
        self.assertEqual(format(12.454), 12.5)
        self.assertEqual(format(datetime(2015, 1, 27, 12, 0, 56, 345)), '2015-01-27 12:00:56')
        self.assertEqual(format('test'), 'test')
        self.assertEqual(format(123), 123)
        self.assertIsNone(format(None))

    def test_format_2(self):
        # test dict, list and tuple with recursion
        cases = ((
            {'a': 1.11, 'b': {'c': 1.11, 'd': {'e': 1.11}}},
            [
                (1, {'a': 1.1, 'b': {'c': 1.11, 'd': {'e': 1.11}}}),
                (2, {'a': 1.1, 'b': {'c': 1.1, 'd': {'e': 1.11}}}),
            ]
        ), (
            [1.11, [1.11, [1.11]]],
            [
                (1, [1.1, [1.11, [1.11]]]),
                (2, [1.1, [1.1, [1.11]]]),
            ]
        ), (
            (1.11, (1.11, (1.11,))),
            [
                (1, (1.1, (1.11, (1.11,)))),
                (2, (1.1, (1.1, (1.11,)))),
            ]
        ), (
            (1.11, [{'a': 1.11, 'b': (1.11, [1.11])}, 1.22]),
            [
                (1, (1.1, [{'a': 1.11, 'b': (1.11, [1.11])}, 1.22])),
                (2, (1.1, [{'a': 1.11, 'b': (1.11, [1.11])}, 1.2])),
                (3, (1.1, [{'a': 1.1, 'b': (1.11, [1.11])}, 1.2])),
                (4, (1.1, [{'a': 1.1, 'b': (1.1, [1.11])}, 1.2])),
            ]
        ))
        for data, data_cases in cases:
            for level, expect in data_cases:
                self.assertEqual(format(data, level), expect)

    def test_get_argument(self):
        # correct arguments
        self.assertEqual(get_argument('hello', str), 'hello')
        self.assertEqual(get_argument('123', int), 123)
        self.assertEqual(get_argument('123.5', float), 123.5)
        self.assertEqual(get_argument('ok', bool), True)
        # wrong arguments
        with self.assertRaises(ValueError):
            get_argument('hello', int)
        with self.assertRaises(TypeError):
            get_argument(None, int)
