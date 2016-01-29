from unittest.mock import patch
from email.mime.text import MIMEText

from tests.base import TestCaseCache
from tasks import send_mail, send_ws
import config


class TestTasks(TestCaseCache):

    @patch('tasks.SMTP.close')
    @patch('tasks.SMTP.sendmail')
    @patch('tasks.SMTP.__init__')
    def test_send_mail_1(self, init, sendmail, close):
        init.return_value = None
        msg = MIMEText('msg', 'text')
        send_mail(msg, ['u1@fakemail'], 'sender@fakemail')
        init.assert_called_once(config.MAIL_SERVER, config.MAIL_PORT)
        sendmail.assert_called_once_with('sender@fakemail', ['u1@fakemail'], msg.as_string())
        close.assert_called_once_with()

    @patch('tasks.SMTP_SSL.close')
    @patch('tasks.SMTP_SSL.sendmail')
    @patch('tasks.SMTP_SSL.login')
    @patch('tasks.SMTP_SSL.starttls')
    @patch('tasks.SMTP_SSL.ehlo')
    @patch('tasks.SMTP_SSL.__init__')
    def test_send_mail_2(self, init, ehlo, starttls, login, sendmail, close):
        init.return_value = None
        msg = MIMEText('msg', 'text')
        config.MAIL_USE_SSL = True
        config.MAIL_USE_TLS = True
        config.MAIL_USERNAME = 'username'
        config.MAIL_PASSWORD = 'password'
        config.DEFAULT_MAIL_SENDER = 'sender@fakemail'
        send_mail(msg, ['u1@fakemail'])
        init.assert_called_once(config.MAIL_SERVER, config.MAIL_PORT)
        ehlo.assert_called_once_with()
        starttls.assert_called_once_with()
        login.assert_called_once_with(user='username', password='password')
        sendmail.assert_called_once_with('sender@fakemail', ['u1@fakemail'], msg.as_string())
        close.assert_called_once_with()

    def test_send_ws(self):
        with patch('tasks.StrictRedis.publish') as mock:
            send_ws('msg')
            mock.assert_called_once_with(config.WS_CHANNEL, 'msg')
