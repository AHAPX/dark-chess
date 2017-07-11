from unittest.mock import patch

from cache import get_cache
import config
from models import User
from tests.base import TestCaseWeb


class TestHandlerAuth(TestCaseWeb):
    url_prefix = '/v2/auth/'

    def test_register_1(self):
        # wrong method
        resp = self.client.get(self.url('register/'))
        self.assertEqual(resp.status_code, 405)
        # validator create error
        resp = self.client.post(self.url('register/'), data={})
        self.assertApiError(resp)
        # validation field error
        resp = self.client.post(self.url('register/'), data={
            'username': 'user1',
            'password': ''
        })
        self.assertApiError(resp)

    def test_register_2(self):
        # successful registration without email
        with patch('connections.send_mail_template') as mock:
            resp = self.client.post(self.url('register/'), data={
                'username': 'user1',
                'password': 'password'
            })
            data = self.load_data(resp)
            self.assertIn('message', data)
            self.assertFalse(mock.called)

    def test_register_3(self):
        # successful registration with email
        with patch('handlers.v2.auth.send_mail_template') as mock,\
                patch('models.User.get_verification') as mock1:
            mock1.return_value = 'token'
            resp = self.client.post(self.url('register/'), data={
                'username': 'user1',
                'password': 'password',
                'email': 'user1@fakemail',
            })
            data = self.load_data(resp)
            self.assertIn('message', data)
            mock.assert_called_once_with('registration', ['user1@fakemail'], data={
                'username': 'user1',
                'url': '{}{}'.format(config.SITE_URL, config.VERIFY_URL),
                'token': 'token'
            })

    def test_get_verification_1(self):
        # try to get verification token without login before
        resp = self.client.get(self.url('verification/'))
        self.assertApiError(resp, 401)

    def test_get_verification_2(self):
        # login and get verification token
        self.login(*self.add_user('user1', 'password', 'user1@fakemail'))
        with patch('handlers.v2.auth.send_mail_template') as mock,\
                patch('models.User.get_verification') as mock1:
            mock1.return_value = 'token'
            resp = self.client.get(self.url('verification/'))
            mock.assert_called_once_with('verification', ['user1@fakemail'], data={
                'username': 'user1',
                'url': '{}{}'.format(config.SITE_URL, config.VERIFY_URL),
                'token': 'token',
            })
        self.load_data(resp)

    def test_verify_1(self):
        # try to verificate with wrong token
        resp = self.client.get(self.url('verification/token/'))
        self.assertApiError(resp, 401)

    def test_verify_2(self):
        # login, get verification token and verify
        self.login(*self.add_user('user1', 'password', 'user1@fakemail'))
        with patch('models.generate_token') as mock:
            mock.return_value = 'token'
            resp = self.client.get(self.url('verification/'))
        resp = self.client.get(self.url('verification/token/'))
        self.load_data(resp)

    def test_reset_1(self):
        self.add_user('user1', 'password', 'user1@fakemail')
        resp = self.client.post(self.url('reset/'), data={'email': 'user2@fakemail'})
        self.assertApiError(resp, 404)

    def test_reset_2(self):
        self.add_user('user1', 'password', 'user1@fakemail')
        resp = self.client.post(self.url('reset/'), data={'email': 'user1@fakemail'})
        self.load_data(resp)

    def test_recover_1(self):
        self.add_user('user1', 'passwd', 'user1@fakemail')
        resp = self.client.post(self.url('recover/token/'), data={'password': 'pass'})
        self.assertApiError(resp)

    def test_recover_2(self):
        self.add_user('user1', 'passwd', 'user1@fakemail')
        resp = self.client.post(self.url('recover/token/'), data={'password': 'password'})
        self.assertApiError(resp, 404)

    def test_recover_3(self):
        self.add_user('user1', 'passwd', 'user1@fakemail')
        resp = self.client.get(self.url('recover/token/'))
        self.assertApiError(resp, 404)

    def test_reset_and_recover(self):
        self.add_user('user1', 'password', 'user1@fakemail')
        with patch('handlers.v2.auth.send_mail_template') as mock,\
                patch('models.generate_token') as mock1:
            mock1.return_value = 'token'
            resp = self.client.post(self.url('reset/'), data={'email': 'user1@fakemail'})
            mock.assert_called_once_with('reset', ['user1@fakemail'], data={
                'username': 'user1',
                'url': '{}{}'.format(config.SITE_URL, config.RECOVER_URL),
                'token': 'token',
            })
            self.load_data(resp)
        resp = self.client.get(self.url('recover/token/'))
        self.load_data(resp)
        resp = self.client.post(self.url('recover/token/'), data={'password': 'password'})
        self.load_data(resp)
        self.assertTrue(User.authenticate('user1', 'password'))

    def test_login_1(self):
        # user not found
        user_data = {
            'username': 'user1',
            'password': 'password',
        }
        resp = self.client.post(self.url('login/'), data=user_data)
        self.assertApiError(resp, 400)

    def test_login_2(self):
        # add user
        self.add_user('user1', 'password', 'user1@fakemail', 'token')
        # not authorized
        resp = self.client.get(self.url('login/'))
        self.assertApiError(resp, 401)
        # login
        user_data = {
            'username': 'user1',
            'password': 'password',
        }
        resp = self.client.post(self.url('login/'), data=user_data)
        data = self.load_data(resp)
        self.assertIn('auth', data)
        # authorized
        resp = self.client.get(self.url('login/'))
        self.assertEqual(self.load_data(resp), {'username': 'user1'})

    def test_logout_1(self):
        # try to logout without login before
        resp = self.client.get(self.url('logout/'))
        self.assertApiError(resp, 401)

    def test_logout_2(self):
        # login and logout
        auth_token = self.login(*self.add_user('user1', 'password', 'user1@fakemail'))
        self.assertIsNotNone(get_cache(auth_token))
        resp = self.client.get(self.url('logout/'))
        data = self.load_data(resp)
        self.assertIn('message', data)
        self.assertIsNone(get_cache(auth_token))
