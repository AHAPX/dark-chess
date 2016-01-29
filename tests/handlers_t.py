from unittest.mock import patch

from tests.base import TestCaseWeb
from cache import get_cache


class TestHandlersMain(TestCaseWeb):

    def test_index(self):
        resp = self.client.get('/')
        data = self.load_data(resp)
        self.assertTrue(data['rc'])
        self.assertIn('message', data)


class TestHandlersAuth(TestCaseWeb):

    def add_user(self, username, password, email, token='token'):
        with patch('models.User.get_verification') as mock:
            mock.return_value = token
            self.client.post('/auth/register', data={
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
        resp = self.client.post('/auth/login', data=user_data)
        data = self.load_data(resp)
        self.client.set_cookie('localhost', 'auth', data['auth'])
        return data['auth']

    def test_register_1(self):
        resp = self.client.get('/auth/register')
        self.assertEqual(resp.status_code, 405)

    def test_register_2(self):
        with patch('connections.send_mail_template') as mock:
            resp = self.client.post('/auth/register', data={
                'username': 'user1',
                'password': 'password'
            })
            data = self.load_data(resp)
            self.assertTrue(data['rc'])
            self.assertIn('message', data)
            self.assertFalse(mock.called)

    def test_register_3(self):
        with patch('handlers.auth.send_mail_template') as mock,\
                patch('models.User.get_verification') as mock1:
            mock1.return_value = 'token'
            resp = self.client.post('/auth/register', data={
                'username': 'user1',
                'password': 'password',
                'email': 'user1@fakemail',
            })
            data = self.load_data(resp)
            self.assertTrue(data['rc'])
            self.assertIn('message', data)
            mock.assert_called_once_with('registration', ['user1@fakemail'], data={
                'username': 'user1',
                'token': 'token'
            })

    def test_login_1(self):
        user_data = {
            'username': 'user1',
            'password': 'password',
        }
        resp = self.client.get('/auth/login', data=user_data)
        self.assertEqual(resp.status_code, 405)
        resp = self.client.post('/auth/login', data=user_data)
        data = self.load_data(resp)
        self.assertFalse(data['rc'])
        self.assertIn('error', data)

    def test_login_2(self):
        self.add_user('user1', 'password', 'user1@fakemail', 'token')
        user_data = {
            'username': 'user1',
            'password': 'password',
        }
        resp = self.client.post('/auth/login', data=user_data)
        data = self.load_data(resp)
        self.assertTrue(data['rc'])
        self.assertIn('auth', data)

    def test_logout_1(self):
        resp = self.client.get('/auth/logout')
        data = self.load_data(resp)
        self.assertFalse(data['rc'])
        self.assertIn('error', data)

    def test_logout_2(self):
        auth_token = self.login(*self.add_user('user1', 'password', 'user1@fakemail'))
        self.assertIsNotNone(get_cache(auth_token))
        resp = self.client.get('/auth/logout')
        data = self.load_data(resp)
        self.assertTrue(data['rc'])
        self.assertIn('message', data)
        self.assertIsNone(get_cache(auth_token))

    def test_get_verification_1(self):
        resp = self.client.get('/auth/verification/')
        data = self.load_data(resp)
        self.assertFalse(data['rc'])
        self.assertIn('error', data)

    def test_get_verification_2(self):
        self.login(*self.add_user('user1', 'password', 'user1@fakemail'))
        with patch('handlers.auth.send_mail_template') as mock,\
                patch('models.User.get_verification') as mock1:
            mock1.return_value = 'token'
            resp = self.client.get('/auth/verification/')
            mock.assert_called_once_with('verification', ['user1@fakemail'], data={
                'username': 'user1',
                'token': 'token',
            })
        self.assertTrue(self.load_data(resp)['rc'])

    def test_verify_1(self):
        resp = self.client.get('/auth/verification/token')
        data = self.load_data(resp)
        self.assertFalse(data['rc'])
        self.assertIn('error', data)

    def test_verify_2(self):
        self.login(*self.add_user('user1', 'password', 'user1@fakemail'))
        with patch('models.generate_token') as mock:
            mock.return_value = 'token'
            resp = self.client.get('/auth/verification/')
        resp = self.client.get('/auth/verification/token')
        self.assertTrue(self.load_data(resp)['rc'])
