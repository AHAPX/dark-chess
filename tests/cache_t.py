import time

from tests.base import TestCaseCache
import consts
from cache import (
    set_cache, get_cache, delete_cache, add_to_queue, get_from_queue,
    get_from_any_queue, get_cache_func_name
)
from helpers import get_prefix


class TestCache(TestCaseCache):

    def test_cache_1(self):
        self.assertEqual(get_cache('nokey'), None)
        set_cache('key', 'data')
        self.assertEqual(get_cache('key'), 'data')
        delete_cache('key')
        self.assertEqual(get_cache('key'), None)

    def test_cache_2(self):
        set_cache('key', 'data', 1)
        self.assertEqual(get_cache('key'), 'data')
        time.sleep(1)
        self.assertEqual(get_cache('key'), None)

    def test_cache_3(self):
        set_cache('key', (1, True, 'test'))
        self.assertEqual(get_cache('key'), (1, True, 'test'))
        set_cache('key', {'k1': 'v1', 'k2': True})
        self.assertEqual(get_cache('key'), {'k1': 'v1', 'k2': True})

    def test_queue_1(self):
        self.assertIsNone(get_from_queue('p1'))
        self.assertIsNone(get_from_queue('p2'))
        add_to_queue('123', 'p2')
        self.assertIsNone(get_from_queue('p1'))
        self.assertEqual(get_from_queue('p2'), '123')
        self.assertIsNone(get_from_queue('p2'))

    def test_queue_2(self):
        _type = consts.TYPE_FAST
        self.assertEqual(get_from_any_queue(_type), (None, None))
        for key in consts.TYPES[_type]['periods'].keys():
            _limit = consts.TYPES[_type]['periods'][key][1]
            add_to_queue('123', get_prefix(_type, _limit))
            self.assertEqual(get_from_any_queue(_type), ('123', _limit))
        self.assertEqual(get_from_any_queue(_type), (None, None))

    def test_get_cache_func_name(self):
        cases = [
            (
                ((1,), {'b': 2}),
                'cached_func_b9ff99622beb5f71274947a159578973'
            ),
            (
                (('str', True), {'c': TestCaseCache()}),
                'cached_func_0a5d39f100f35512e2d07b9cd28dadf6'
            ),
        ]
        for (args, kwargs), expect in cases:
            self.assertEqual(get_cache_func_name('fn', *args, **kwargs), expect)
