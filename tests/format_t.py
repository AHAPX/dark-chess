from datetime import datetime

from tests.base import TestCaseBase
from format import format, get_argument


class TestFormat(TestCaseBase):

    def test_format(self):
        self.assertEqual(format(12.454), 12.5)
        self.assertEqual(format(datetime(2015, 1, 27, 12, 0, 56, 345)), '2015-01-27 12:00:56')
        self.assertEqual(format('test'), 'test')
        self.assertEqual(format(123), 123)
        self.assertIsNone(format(None))

    def test_get_argument(self):
        self.assertEqual(get_argument('hello', str), 'hello')
        self.assertEqual(get_argument('123', int), 123)
        self.assertEqual(get_argument('123.5', float), 123.5)
        self.assertEqual(get_argument('ok', bool), True)
        with self.assertRaises(ValueError):
            get_argument('hello', int)
        with self.assertRaises(TypeError):
            get_argument(None, int)
