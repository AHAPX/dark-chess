from unittest.mock import patch

from tests.base import TestCaseWeb
from models import User
from cache import get_cache
import config


class TestHandlerAuth(TestCaseWeb):
    url_prefix = '/v1/auth/'

    def test_register_1(self):
        # wrong method
        resp = self.client.get(self.url('register'))
        self.assertEqual(resp.status_code, 405)
        # validator create error
        resp = self.client.post(self.url('register'), data={})
        data = self.load_data(resp)
        self.assertFalse(data['rc'])
        self.assertIn('error', data)
        # validation field error
        resp = self.client.post(self.url('register'), data={
            'username': 'user1',
            'password': ''
        })
        data = self.load_data(resp)
        self.assertFalse(data['rc'])
        self.assertIn('error', data)

    def test_register_2(self):
        # successful registration without email
        with patch('connections.send_mail_template') as mock:
            resp = self.client.post(self.url('register'), data={
                'username': 'user1',
                'password': 'password'
            })
            data = self.load_data(resp)
            self.assertTrue(data['rc'])
            self.assertIn('message', data)
            self.assertFalse(mock.called)

    def test_register_3(self):
        # successful registration with email
        with patch('handlers.v1.auth.send_mail_template') as mock,\
                patch('models.User.get_verification') as mock1:
            mock1.return_value = 'token'
            resp = self.client.post(self.url('register'), data={
                'username': 'user1',
                'password': 'password',
                'email': 'user1@fakemail',
            })
            data = self.load_data(resp)
            self.assertTrue(data['rc'])
            self.assertIn('message', data)
            mock.assert_called_once_with('registration', ['user1@fakemail'], data={
                'username': 'user1',
                'url': '{}{}'.format(config.SITE_URL, config.VERIFY_URL),
                'token': 'token'
            })

    def test_login_1(self):
        user_data = {
            'username': 'user1',
            'password': 'password',
        }
        # wrong method
        resp = self.client.get(self.url('login'), data=user_data)
        self.assertEqual(resp.status_code, 405)
        # user not found
        resp = self.client.post(self.url('login'), data=user_data)
        data = self.load_data(resp)
        self.assertFalse(data['rc'])
        self.assertIn('error', data)

    def test_login_2(self):
        # add user and login
        self.add_user('user1', 'password', 'user1@fakemail', 'token')
        user_data = {
            'username': 'user1',
            'password': 'password',
        }
        resp = self.client.post(self.url('login'), data=user_data)
        data = self.load_data(resp)
        self.assertTrue(data['rc'])
        self.assertIn('auth', data)

    def test_logout_1(self):
        # try to logout without login before
        resp = self.client.get(self.url('logout'))
        data = self.load_data(resp)
        self.assertFalse(data['rc'])
        self.assertIn('error', data)

    def test_logout_2(self):
        # login and logout
        auth_token = self.login(*self.add_user('user1', 'password', 'user1@fakemail'))
        self.assertIsNotNone(get_cache(auth_token))
        resp = self.client.get(self.url('logout'))
        data = self.load_data(resp)
        self.assertTrue(data['rc'])
        self.assertIn('message', data)
        self.assertIsNone(get_cache(auth_token))

    def test_get_verification_1(self):
        # try to get verification token without login before
        resp = self.client.get(self.url('verification'))
        data = self.load_data(resp)
        self.assertFalse(data['rc'])
        self.assertIn('error', data)

    def test_get_verification_2(self):
        # login and get verification token
        self.login(*self.add_user('user1', 'password', 'user1@fakemail'))
        with patch('handlers.v1.auth.send_mail_template') as mock,\
                patch('models.User.get_verification') as mock1:
            mock1.return_value = 'token'
            resp = self.client.get(self.url('verification'))
            mock.assert_called_once_with('verification', ['user1@fakemail'], data={
                'username': 'user1',
                'url': '{}{}'.format(config.SITE_URL, config.VERIFY_URL),
                'token': 'token',
            })
        self.assertTrue(self.load_data(resp)['rc'])

    def test_verify_1(self):
        # try to verificate with wrong token
        resp = self.client.get(self.url('verification/token'))
        data = self.load_data(resp)
        self.assertFalse(data['rc'])
        self.assertIn('error', data)

    def test_verify_2(self):
        # login, get verification token and verify
        self.login(*self.add_user('user1', 'password', 'user1@fakemail'))
        with patch('models.generate_token') as mock:
            mock.return_value = 'token'
            resp = self.client.get(self.url('verification'))
        resp = self.client.get(self.url('verification/token'))
        self.assertTrue(self.load_data(resp)['rc'])

    def test_reset_1(self):
        self.add_user('user1', 'password', 'user1@fakemail')
        resp = self.client.post(self.url('reset'), data={'email': 'user1'})
        data = self.load_data(resp)
        self.assertFalse(data['rc'])
        self.assertIn('error', data)

    def test_reset_2(self):
        self.add_user('user1', 'password', 'user1@fakemail')
        resp = self.client.post(self.url('reset'), data={'email': 'user2@fakemail'})
        data = self.load_data(resp)
        self.assertFalse(data['rc'])
        self.assertIn('error', data)

    def test_recover_1(self):
        self.add_user('user1', 'passwd', 'user1@fakemail')
        resp = self.client.post(self.url('recover/token'), data={'password': 'pass'})
        data = self.load_data(resp)
        self.assertFalse(data['rc'])
        self.assertIn('error', data)

    def test_recover_2(self):
        self.add_user('user1', 'passwd', 'user1@fakemail')
        resp = self.client.post(self.url('recover/token'), data={'password': 'password'})
        data = self.load_data(resp)
        self.assertFalse(data['rc'])
        self.assertIn('error', data)

    def test_recover_3(self):
        self.add_user('user1', 'passwd', 'user1@fakemail')
        resp = self.client.get(self.url('recover/token'))
        data = self.load_data(resp)
        self.assertFalse(data['rc'])
        self.assertIn('error', data)

    def test_reset_and_recover(self):
        self.add_user('user1', 'password', 'user1@fakemail')
        with patch('handlers.v1.auth.send_mail_template') as mock,\
                patch('models.generate_token') as mock1:
            mock1.return_value = 'token'
            resp = self.client.post(self.url('reset'), data={'email': 'user1@fakemail'})
            mock.assert_called_once_with('reset', ['user1@fakemail'], data={
                'username': 'user1',
                'url': '{}{}'.format(config.SITE_URL, config.RECOVER_URL),
                'token': 'token',
            })
            self.assertTrue(self.load_data(resp)['rc'])
        resp = self.client.get(self.url('recover/token'))
        self.assertTrue(self.load_data(resp)['rc'])
        resp = self.client.post(self.url('recover/token'), data={'password': 'password'})
        self.assertTrue(self.load_data(resp)['rc'])
        self.assertTrue(User.authenticate('user1', 'password'))

    def test_authorized(self):
        resp = self.client.get(self.url('authorized'))
        self.assertFalse(self.load_data(resp)['rc'])
        self.login(*self.add_user('user1', 'password', 'user1@fakemail'))
        resp = self.client.get(self.url('authorized'))
        data = self.load_data(resp)
        self.assertEqual(data, {'rc': True, 'username': 'user1'})
