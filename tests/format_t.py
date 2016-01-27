from datetime import datetime

from tests.base import TestCaseBase
from format import format


class TestFormat(TestCaseBase):

    def test_format(self):
        self.assertEqual(format(12.454), 12.5)
        self.assertEqual(format(datetime(2015, 1, 27, 12, 0, 56, 345)), '2015-01-27 12:00:56')
        self.assertEqual(format('test'), 'test')
        self.assertEqual(format(123), 123)
        self.assertIsNone(format(None))
