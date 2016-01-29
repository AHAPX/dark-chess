from validate_email import validate_email

from models import User
from helpers import get_request_arg
import errors


class BaseValidator(object):
    fields = {}

    def __init__(self, request):
        self.form, self._error = {}, None
        for name, (_type, required) in self.fields.items():
            value = get_request_arg(request, name)
            if required and value is None:
                raise errors.ValidationRequiredError(name)
            if value is not None:
                try:
                    value = _type(value)
                except (TypeError, ValueError):
                    raise errors.ValidationError(name)
            self.form[name] = value

    def is_valid(self):
        self._error = None
        return True

    def error(self, error):
        self._error = error
        return False

    def get_error(self):
        return self._error


class RegistrationValidator(BaseValidator):
    fields = {
        'username': (str, True),
        'password': (str, True),
        'email': (str, False),
    }

    def is_valid(self):
        if len(self.form['username']) < 4:
            return self.error('username must be at least 4 characters')
        if len(self.form['password']) < 8:
            return self.error('password must be at least 8 characters')
        if User.select().where(User.username == self.form['username']).count():
            return self.error('username is already in use')
        if self.form['email']:
            if not validate_email(self.form['email']):
                return self.error('email is not valid')
            if User.select().where(User.email == self.form['email']).count():
                return self.error('email is already in use')
        return super(RegistrationValidator, self).is_valid()


class LoginValidator(BaseValidator):
    fields = {
        'username': (str, True),
        'password': (str, True),
    }
