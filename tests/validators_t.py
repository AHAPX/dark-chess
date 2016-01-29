from tests.base import TestCaseDB, MockRequest
from validators import BaseValidator, RegistrationValidator, LoginValidator
from models import User
import errors


class TestValidators(TestCaseDB):

    def test_base(self):
        # init fields
        BaseValidator.fields = {
            'f1': (str, True),
            'f2': (int, False),
        }
        # try to create validator without reqired field
        with self.assertRaises(errors.ValidationRequiredError, msg='f1'):
            BaseValidator(MockRequest(form={'f2': '42'}))
        # try to create validator with wrong type
        with self.assertRaises(errors.ValidationError, msg='f2'):
            BaseValidator(MockRequest(form={'f1': 'v1', 'f2': 'v2'}))
        # create validator without not required field and check it
        val = BaseValidator(MockRequest(form={'f1': 'v1'}))
        self.assertEqual(val.form, {'f1': 'v1', 'f2': None})
        # create validator with all fields and check it
        val = BaseValidator(MockRequest(form={'f1': 'v1', 'f2': '42'}))
        self.assertEqual(val.form, {'f1': 'v1', 'f2': 42})
        # test is_valid and get_error
        self.assertIsNone(val.get_error())
        self.assertFalse(val.error('test'))
        self.assertEqual(val.get_error(), 'test')
        self.assertTrue(val.is_valid())
        self.assertIsNone(val.get_error())

    def assertValidations(self, validator, fields, cases):
        for (values), is_valid, expect in cases:
            request = MockRequest(form={
                fields[i]: values[i] for i in range(len(fields))
            })
            val = validator(request)
            self.assertEqual(val.is_valid(), is_valid)
            if expect:
                self.assertIn(expect, val.get_error())

    def test_registration(self):
        User.create(username='user1', password='password', email='u1@fakemail')
        cases = [
            (('u1', 'password', 'u2@fakemail'), False, 'username'),
            (('user2', 'pass', 'u2@fakemail'), False, 'password'),
            (('user1', 'password', 'u2@fakemail'), False, 'username'),
            (('user2', 'password', 'u2'), False, 'email'),
            (('user2', 'password', 'u1@fakemail'), False, 'email'),
            (('user2', 'password', 'u2@fakemail'), True, None),
            (('user2', 'password', None), True, None),
        ]
        self.assertValidations(
            RegistrationValidator, ('username', 'password', 'email'), cases
        )

    def test_login(self):
        cases = [
            (('user1', 'password'), True, None),
        ]
        self.assertValidations(LoginValidator, ('username', 'password'), cases)
