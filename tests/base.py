import unittest
from unittest.mock import patch
from urllib.parse import urljoin
import inspect
import sys
import json

from playhouse.test_utils import test_database
from peewee import SqliteDatabase, Model
from fakeredis import FakeStrictRedis

import cache
from models import User, Game, Move
from app import app


test_db = SqliteDatabase(':memory:')


class TestCaseBase(unittest.TestCase):

    def assertComprateDicts(self, data, expect):
        for k1, v1 in expect.items():
            if isinstance(v1, dict):
                for k2, v2 in v1.items():
                    self.assertEqual(data[k1][k2], v2)
            else:
                self.assertEqual(data[k1], v1)
        for key in data.keys():
            self.assertIn(key, expect)


class TestCaseCache(TestCaseBase):

    @classmethod
    def setUpClass(cls):
        cache.redis = FakeStrictRedis()

    def setUp(self):
        cache.redis.flushdb()
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
    url_prefix = '/v1/'

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        super(TestCaseWeb, self).setUp()

    def url(self, url):
        return urljoin(self.url_prefix, url)

    def load_data(self, response):
        self.assertEqual(response.status_code, 200)
        return json.loads(response.data.decode())

    def add_user(self, username, password, email, token='token'):
        with patch('models.User.get_verification') as mock:
            mock.return_value = token
            self.client.post('/v1/auth/register', data={
                'username': username,
                'password': password,
                'email': email,
            })
            return username, password

    def login(self, username, password):
        user_data = {
            'username': username,
            'password': password,
        }
        resp = self.client.post('/v1/auth/login', data=user_data)
        data = self.load_data(resp)
        self.client.set_cookie('localhost', 'auth', data['auth'])
        return data['auth']


class MockRequest(object):

    def __init__(self, form={}, args={}, json=None):
        self.form = form
        self.args = args
        self.json = json
