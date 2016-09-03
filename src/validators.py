from validate_email import validate_email

from models import User
from helpers import get_request_arg, coors2pos, onBoard
import errors
from format import get_argument
import consts
import config


class BaseValidator(object):
    fields = {}
    cleaned_fields = {}

    def __init__(self, request):
        self.form, self.cleaned_data, self._error = {}, {}, None
        for name, params in self.fields.items():
            value = get_request_arg(request, name)
            if params.get('required') and value is None:
                raise errors.ValidationRequiredError(name)
            if value is not None:
                try:
                    value = get_argument(value, params['type'])
                except (TypeError, ValueError):
                    raise errors.ValidationError(name)
            else:
                value = params.get('default')
            self.form[name] = value

    def is_valid(self):
        self._error = None
        if not self.cleaned_fields:
            self.cleaned_data = self.form
        return True

    def error(self, error):
        self._error = error
        return False

    def get_error(self):
        return self._error


class RegistrationValidator(BaseValidator):
    fields = {
        'username': dict(type=str, required=True),
        'password': dict(type=str, required=True),
        'email': dict(type=str),
    }

    def is_valid(self):
        if len(self.form['username']) < 4:
            return self.error('username must be at least 4 characters')
        if self.form['username'] == 'anonymous':
            return self.error('username cannot be anonymous')
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


class ResetValidator(BaseValidator):
    fields = {
        'email': dict(type=str, required=True),
    }

    def is_valid(self):
        if not validate_email(self.form['email']):
            return self.error('email is not valid')
        return super(ResetValidator, self).is_valid()


class RecoverValidator(BaseValidator):
    fields = {
        'password': dict(type=str, required=True),
    }

    def is_valid(self):
        if len(self.form['password']) < 8:
            return self.error('password must be at least 8 characters')
        return super(RecoverValidator, self).is_valid()


class LoginValidator(BaseValidator):
    fields = {
        'username': dict(type=str, required=True),
        'password': dict(type=str, required=True),
    }


class GameNewValidator(BaseValidator):
    fields = {
        'type': dict(type=str, default='no limit'),
        'limit': dict(type=str),
    }
    cleaned_fields = {
        'type': dict(type=int),
        'limit': dict(type=int),
    }

    def is_valid(self):
        game_type = consts.TYPES_NAMES.get(self.form['type'])
        if game_type is None:
            return self.error('{} is not available type'.format(self.form['type']))
        if game_type != consts.TYPE_NOLIMIT and self.form['limit']:
            try:
                game_limit = consts.TYPES[game_type]['periods'][self.form['limit']][1]
            except:
                return self.error('{} limit is not available for {} game'.format(
                    self.form['limit'], self.form['type']
                ))
        else:
            game_limit = None
        self.cleaned_data = {
            'type': game_type,
            'limit': game_limit,
        }
        return super(GameNewValidator, self).is_valid()


class GameMoveValidator(BaseValidator):
    fields = {
        'move': dict(type=str, required=True)
    }
    cleaned_fields = {
        'coor1': dict(type=str),
        'coor2': dict(type=str),
    }

    def is_valid(self):
        coors = self.form['move'].split('-')
        if len(coors) != 2:
            return self.error('move format must be like e2-e4')
        try:
            for coor in coors:
                if not onBoard(*coors2pos(coor)):
                    raise ValueError(coor)
        except ValueError:
            return self.error('some coordinate is incorrect')
        self.cleaned_data = {
            'coor1': coors[0],
            'coor2': coors[1],
        }
        return super(GameMoveValidator, self).is_valid()


class MessageValidator(BaseValidator):
    fields = {
        'text': dict(type=str)
    }

    def is_valid(self):
        if len(self.form['text']) > config.MAX_LENGTH_MESSAGE:
            return self.error('message has {} symbols, but it cannot be more that {}'.format(
                len(self.form['text']), config.MAX_LENGTH_MESSAGE))
        return super(MessageValidator, self).is_valid()
