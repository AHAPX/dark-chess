from unittest.mock import patch
import json

from tests.base import TestCaseBase
from connections import check_email, send_mail, send_mail_template, send_ws
from app import app


class TestConnections(TestCaseBase):

    def test_check_email(self):
        self.assertEqual(check_email('user1@mail'), ['user1@mail'])
        self.assertEqual(check_email(['user1@mail']), ['user1@mail'])
        with self.assertRaises(ValueError):
            check_email(123)

    @patch('connections.json.dumps')
    @patch('connections.StrictRedis.publish')
    def test_send_mail(self, publish, dumps):
        dumps.return_value = 'SMTP_MSG'
        send_mail('user1@mail', 'subj', 'body', 'html', 'user2@mail')
        publish.assert_called_once_with(app.config['SMTP_BROKER_CHANNEL'], 'SMTP_MSG')

    @patch('connections.render_template')
    @patch('connections.send_mail')
    def test_send_mail_template(self, send_mail, render_template):
        with app.test_request_context():
            send_mail_template('registration', ['user1@mail'])
        send_mail.assert_called_once()
        self.assertEqual(render_template.call_count, 3)

    @patch('connections.json.dumps')
    @patch('connections.StrictRedis.publish')
    def test_send_ws(self, publish, dumps):
        dumps.return_value = 'WS_MSG'
        send_ws('test', 'sig', 'tag')
        publish.assert_called_once_with(app.config['WS_BROKER_CHANNEL'], 'WS_MSG')
