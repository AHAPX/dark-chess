from unittest.mock import patch
import json

import config
from tests.base import TestCaseBase
from connections import fill_msg, send_mail, send_mail_template, send_ws
from app import app


class TestConnections(TestCaseBase):

    def test_fill_msg(self):
        expect_1 = {
            'Subject': '{}subj'.format(config.MAIL_SUBJECT_PREFIX),
            'From': config.DEFAULT_MAIL_SENDER,
            'To': 'user1@mail',
            'Cc': ['user2@mail'],
        }
        self.assertEqual(fill_msg({}, 'subj', ['user1@mail', 'user2@mail']), expect_1)
        expect_2 = {
            'Subject': '{}subj'.format(config.MAIL_SUBJECT_PREFIX),
            'From': 'sender@mail',
            'To': 'user1@mail',
        }
        self.assertEqual(fill_msg({}, 'subj', ['user1@mail'], 'sender@mail'), expect_2)

    @patch('connections.tasks.send_mail.delay')
    def test_send_mail(self, delay):
        send_mail('subj', 'body', ['user1@mail'])
        delay.assert_called_once()

    @patch('connections.render_template')
    @patch('connections.tasks.send_mail.delay')
    def test_send_mail_template(self, delay, render_template):
        with app.test_request_context():
            send_mail_template('registration', ['user1@mail'])
        delay.assert_called_once()
        self.assertEqual(render_template.call_count, 3)

    @patch('connections.tasks.send_ws.delay')
    def test_send_ws(self, delay):
        send_ws('test', 'sig', 'tag')
        msg = {'message': {'message': 'test', 'signal': 'sig'}, 'tags': ['tag']}
        delay.assert_called_once_with(json.dumps(msg))
