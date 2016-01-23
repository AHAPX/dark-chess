import unittest
import time

from cache import set_cache, get_cache, delete_cache


class TestCache(unittest.TestCase):

    def test_cache_1(self):
        self.assertEqual(get_cache('nokey'), None)
        set_cache('key', 'data')
        self.assertEqual(get_cache('key'), 'data')
        delete_cache('key')
        self.assertEqual(get_cache('key'), None)

    def test_cache_2(self):
        set_cache('key', 'data', 2)
        self.assertEqual(get_cache('key'), 'data')
        time.sleep(2)
        self.assertEqual(get_cache('key'), None)
