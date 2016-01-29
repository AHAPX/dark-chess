import unittest
import inspect
import sys
import json

from playhouse.test_utils import test_database
from peewee import SqliteDatabase, Model

from models import User, Game, Move
from cache import redis
from handlers import app


test_db = SqliteDatabase(':memory:')


class TestCaseBase(unittest.TestCase):

    def compare_dicts(self, data, expect):
        for k1, v1 in expect.items():
            self.assertIn(k1, data)
        for k2, v2 in v1.items():
            self.assertEqual(data[k1][k2], v2)
        for key in data.keys():
            self.assertIn(key, expect)


class TestCaseCache(TestCaseBase):

    def setUp(self):
        redis.flushdb()
        super(TestCaseCache, self).setUp()


class TestCaseDB(TestCaseCache):

    def run(self, result=None):
        model_classes = [
            m[1] for m in inspect.getmembers(sys.modules['models'], inspect.isclass)
            if issubclass(m[1], Model) and m[1] != Model
        ]
        with test_database(test_db, model_classes):
            super(TestCaseDB, self).run(result)


class TestCaseWeb(TestCaseDB):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        super(TestCaseWeb, self).setUp()

    def load_data(self, response):
        self.assertEqual(response.status_code, 200)
        return json.loads(response.data.decode())


class MockRequest(object):

    def __init__(self, form={}, args={}, json=None):
        self.form = form
        self.args = args
        self.json = json
