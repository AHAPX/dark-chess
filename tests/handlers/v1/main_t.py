from unittest.mock import patch

from tests.base import TestCaseWeb, app


class TestHandlerMain(TestCaseWeb):
    url_prefix = '/v1/'

    def test_index(self):
        resp = self.client.get(self.url(''))
        data = self.load_data(resp)
        self.assertTrue(data['rc'])
        self.assertIn('message', data)

    @patch('handlers.v1.main.send_message')
    def test_server_error_1(self, send_message):
        app.config['DEBUG'] = False
        send_message.side_effect = ValueError('value_err')
        with self.assertLogs('app', level='CRITICAL'):
            resp = self.client.get(self.url(''))
            self.assertEqual(resp.status_code, 500)

    @patch('handlers.v1.main.send_message')
    def test_server_error_2(self, send_message):
        app.config['DEBUG'] = True
        send_message.side_effect = ValueError('value_err')
        with self.assertLogs('app', level='CRITICAL'),\
                self.assertRaises(ValueError, msg='value_err'):
            self.client.get(self.url(''))
