from unittest.mock import patch, call

from flask import request, make_response

from errors import APIUnauthorized, APIForbidden, APINotFound, CellIsBusyError
from handlers.v2.base import RestBase
from tests.base import TestCaseWeb


class FakeRest(RestBase):
    def get(self):
        return {'get': 'test'}

    def post(self):
        raise APIUnauthorized

    def put(self):
        raise APIForbidden

    def delete(self):
        raise APINotFound('some')


class FakeRest1(RestBase):
    def get(self):
        raise CellIsBusyError

    def post(self):
        raise TypeError('error')


class TestHandlerBase(TestCaseWeb):
    def test_options(self):
        r = FakeRest()
        with patch('handlers.v2.base.request') as mock:
            mock.method = 'OPTIONS'
            self.assertIsNotNone(r().headers)

    def test_get(self):
        r = FakeRest()
        with patch('handlers.v2.base.request') as mock:
            mock.method = 'GET'
            data = self.load_data(r())
            self.assertEqual(data, {'get': 'test'})

    def test_post(self):
        r = FakeRest()
        with patch('handlers.v2.base.request') as mock,\
                patch('handlers.v2.base.abort') as mock1,\
                patch('handlers.v2.base.make_response') as mock2:
            mock.method = 'POST'
            self.assertEqual(self.load_data(r()), {})
            self.assertEqual(mock1.call_count, 1)
            mock2.assert_has_calls([call('not authorized', 401)])

    def test_put(self):
        r = FakeRest()
        with patch('handlers.v2.base.request') as mock,\
                patch('handlers.v2.base.abort') as mock1,\
                patch('handlers.v2.base.make_response') as mock2:
            mock.method = 'PUT'
            self.assertEqual(self.load_data(r()), {})
            self.assertEqual(mock1.call_count, 1)
            mock2.assert_has_calls([call('forbidden', 403)])

    def test_delete(self):
        r = FakeRest()
        with patch('handlers.v2.base.request') as mock,\
                patch('handlers.v2.base.abort') as mock1,\
                patch('handlers.v2.base.make_response') as mock2:
            mock.method = 'DELETE'
            self.assertEqual(self.load_data(r()), {})
            self.assertEqual(mock1.call_count, 1)
            mock2.assert_has_calls([call('some not found', 404)])

    def test_get_1(self):
        r = FakeRest1()
        with patch('handlers.v2.base.request') as mock,\
                patch('handlers.v2.base.abort') as mock1,\
                patch('handlers.v2.base.make_response') as mock2:
            mock.method = 'GET'
            self.assertEqual(self.load_data(r()), {})
            self.assertEqual(mock1.call_count, 1)
            mock2.assert_has_calls([call('you cannot cut your figure', 400)])

    def test_post_1(self):
        r = FakeRest1()
        with patch('handlers.v2.base.request') as mock,\
                patch('handlers.v2.base.abort') as mock1:
            mock.method = 'POST'
            with self.assertLogs('handlers.v2.base', level='ERROR'):
                self.assertEqual(self.load_data(r()), {})
            mock1.assert_has_calls([call(500)])

    def test_put_1(self):
        r = FakeRest1()
        with patch('handlers.v2.base.request') as mock,\
                patch('handlers.v2.base.abort') as mock1:
            mock.method = 'PUT'
            self.assertEqual(self.load_data(r()), {})
            mock1.assert_has_calls([call(405)])
