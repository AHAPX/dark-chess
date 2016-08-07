from tests.base import TestCaseDB, MockRequest
from validators import (
    BaseValidator, RegistrationValidator, LoginValidator, GameNewValidator,
    GameMoveValidator, ResetValidator, RecoverValidator
)
from models import User
import errors
from consts import TYPE_NOLIMIT, TYPE_SLOW, TYPE_FAST


class TestValidators(TestCaseDB):

    def test_base(self):
        # init fields
        BaseValidator.fields = {
            'f1': dict(type=str, required=True),
            'f2': dict(type=int),
            'f3': dict(type=str, default='ok'),
        }
        # try to create validator without reqired field
        with self.assertRaises(errors.ValidationRequiredError, msg='f1'):
            BaseValidator(MockRequest(form={'f2': '42'}))
        # try to create validator with wrong type
        with self.assertRaises(errors.ValidationError, msg='f2'):
            BaseValidator(MockRequest(form={'f1': 'v1', 'f2': 'v2'}))
        # create validator without not required field and check it
        val = BaseValidator(MockRequest(form={'f1': 'v1'}))
        self.assertEqual(val.form, {'f1': 'v1', 'f2': None, 'f3': 'ok'})
        # create validator with all fields and check it
        val = BaseValidator(MockRequest(form={'f1': 'v1', 'f2': '42'}))
        self.assertEqual(val.form, {'f1': 'v1', 'f2': 42, 'f3': 'ok'})
        # test is_valid and get_error
        self.assertIsNone(val.get_error())
        self.assertFalse(val.error('test'))
        self.assertEqual(val.get_error(), 'test')
        self.assertTrue(val.is_valid())
        self.assertIsNone(val.get_error())
        self.assertEqual(val.form, val.cleaned_data)

    def assertValidations(self, validator, fields, cases):
        for (values), is_valid, expect, (cd) in cases:
            request = MockRequest(form={
                fields[i]: values[i] for i in range(len(fields))
            })
            val = validator(request)
            self.assertEqual(val.is_valid(), is_valid)
            if expect:
                self.assertIn(expect, val.get_error())
            if cd:
                self.assertEqual(val.cleaned_data, cd)

    def test_registration(self):
        User.create(username='user1', password='password', email='u1@fakemail')
        cases = [
            (('u1', 'password', 'u2@fakemail'), False, 'username', None),
            (('user2', 'pass', 'u2@fakemail'), False, 'password', None),
            (('user1', 'password', 'u2@fakemail'), False, 'username', None),
            (('user2', 'password', 'u2'), False, 'email', None),
            (('user2', 'password', 'u1@fakemail'), False, 'email', None),
            (('user2', 'password', 'u2@fakemail'), True, None, None),
            (('user2', 'password', None), True, None, None),
        ]
        self.assertValidations(
            RegistrationValidator, ('username', 'password', 'email'), cases
        )

    def test_reset(self):
        User.create(username='user1', password='password', email='u1@fakemail')
        cases = [
            (('u1',), False, 'not valid', None),
            (('u1@fakemail',), True, None, {'email': 'u1@fakemail'}),
        ]
        self.assertValidations(ResetValidator, ('email',), cases)

    def test_recover(self):
        cases = [
            (('pass',), False, 'password', None),
            (('password',), True, None, {'password': 'password'}),
        ]
        self.assertValidations(RecoverValidator, ('password',), cases)

    def test_login(self):
        cases = [
            (('user1', 'password'), True, None, None),
        ]
        self.assertValidations(LoginValidator, ('username', 'password'), cases)

    def test_new_game(self):
        cases = [
            (('urgent', None), False, 'type', None),
            (('fast', 'm'), False, 'limit', None),
            (('slow', '1d'), True, None, {'type': TYPE_SLOW, 'limit': 86400}),
            (('fast', '5m'), True, None, {'type': TYPE_FAST, 'limit': 300}),
            ((None, None), True, None, {'type': TYPE_NOLIMIT, 'limit': None}),
        ]
        self.assertValidations(GameNewValidator, ('type', 'limit'), cases)

    def test_move(self):
        cases = [
            (('e0-e4',), False, 'coordinate', None),
            (('e2-j4',), False, 'coordinate', None),
            (('0-0',), False, 'coordinate', None),
            (('e2e4',), False, 'move', None),
            (('e2-e4-e6',), False, 'move', None),
            (('e2-e4',), True, None, {'coor1': 'e2', 'coor2': 'e4'})
        ]
        self.assertValidations(GameMoveValidator, ('move',), cases)
