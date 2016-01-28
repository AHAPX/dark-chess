from tests import TestCaseDB
from validators import BaseValidator, RegistrationValidator, LoginValidator
from models import User


class TestValidators(TestCaseDB):

    def test_base(self):
        val = BaseValidator()
        self.assertIsNone(val.get_error())
        self.assertFalse(val.error('test'))
        self.assertEqual(val.get_error(), 'test')
        self.assertTrue(val.is_valid())
        self.assertIsNone(val.get_error())

    def test_registration(self):
        User.create(username='user1', password='password', email='u1@fakemail')
        cases = [
            (('u1', 'password', 'u2@fakemail'), 'username'),
            (('user2', 'pass', 'u2@fakemail'), 'password'),
            (('user1', 'password', 'u2@fakemail'), 'username'),
            (('user2', 'password', 'u2'), 'email'),
            (('user2', 'password', 'u1@fakemail'), 'email'),
        ]
        for (username, password, email), expect in cases:
            val = RegistrationValidator(username, password, email)
            self.assertFalse(val.is_valid())
            self.assertIn(expect, val.get_error())
        val = RegistrationValidator('user2', 'password', 'u2@fakemail')
        self.assertTrue(val.is_valid())

    def test_login(self):
        cases = [
            ((None, 'password'), 'username'),
            (('user1', None), 'password'),
        ]
        for (username, password), expect in cases:
            val = LoginValidator(username, password)
            self.assertFalse(val.is_valid())
            self.assertIn(expect, val.get_error())
        val = LoginValidator('user1', 'password')
        self.assertTrue(val.is_valid())
