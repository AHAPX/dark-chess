from validate_email import validate_email

from models import User


class BaseValidator(object):
    _error = None
    form = {}

    def is_valid(self):
        return True

    def error(self, error):
        self._error = error
        return False

    def get_error(self):
        return self._error


class RegistrationValidator(BaseValidator):

    def __init__(self, username, password, email=None):
        self.form = {
            'username': username,
            'password': password,
            'email': email
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
        return True


class LoginValidator(BaseValidator):

    def __init__(self, username, password):
        self.form = {
            'username': username,
            'password': password,
        }

    def is_valid(self):
        if self.form['username'] is None or self.form['password'] is None:
            return self.error('username or password is incorrect')
        return True
