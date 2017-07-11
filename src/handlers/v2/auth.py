import datetime
from urllib.parse import urljoin

from flask import request, make_response, jsonify

import config
from connections import send_mail_template, send_ws
from errors import APIException, APIUnauthorized, APINotFound, ValidationError
from decorators import validate
from handlers.v2.base import RestBase
from cache import delete_cache
from models import User
from validators import RegistrationValidator, LoginValidator, ResetValidator, RecoverValidator


class RestRegister(RestBase):
    @validate(RegistrationValidator)
    def post(self):
        username = self.data['username']
        password = self.data['password']
        email = self.data['email']
        user = User.add(username, password, email)
        if email:
            token = user.get_verification()
            data = {
                'username': username,
                'url': urljoin(config.SITE_URL, config.VERIFY_URL),
                'token': token,
            }
            send_mail_template('registration', [email], data=data)
        return 'registration successful'


class RestVerification(RestBase):
    auth_required = True

    def get(self):
        try:
            token = request.user.get_verification()
        except Exception as e:
            raise APIException(e.message)
        data = {
            'username': request.user.username,
            'url': urljoin(config.SITE_URL, config.VERIFY_URL),
            'token': token,
        }
        send_mail_template('verification', [request.user.email], data=data)
        return 'send verification email'


class RestVerificationConfirm(RestBase):
    auth_required = True

    def get(self, token):
        user = User.get_by_token(token)
        if user:
            user.verify()
            delete_cache(token)
            return 'verification completed'
        raise APINotFound('token')


class RestLogin(RestBase):
    def get(self):
        if request.user:
            return {'username': request.user.username}
        raise APIUnauthorized

    @validate(LoginValidator)
    def post(self):
        username = self.data['username']
        password = self.data['password']
        token = User.authenticate(username, password)
        if token:
            response = make_response(jsonify({'auth': token}))
            expire_date = datetime.datetime.now() + datetime.timedelta(seconds=config.SESSION_TIME)
            response.set_cookie('auth', token, expires=expire_date)
            return response
        raise ValidationError('username or password incorrect')


class RestReset(RestBase):
    @validate(ResetValidator)
    def post(self):
        try:
            user = User.get(User.email == self.data['email'])
        except User.DoesNotExist:
            raise APINotFound('hey email')
        token = user.get_reset()
        data = {
            'username': user.username,
            'url': urljoin(config.SITE_URL, config.RECOVER_URL),
            'token': token,
        }
        send_mail_template('reset', [user.email], data=data)
        return 'send recover email'


class RestRecover(RestBase):
    def get(self, token):
        user = User.get_by_token(token)
        if not user:
            raise APINotFound('token')
        return 'token is found'

    @validate(RecoverValidator)
    def post(self, token):
        user = User.get_by_token(token)
        if not user:
            raise APINotFound('token')
        user.set_password(self.data['password'])
        user.save()
        delete_cache(token)
        return 'password changed'


class RestLogout(RestBase):
    auth_required = True

    def get(self):
        delete_cache(request.auth)
        response = make_response(jsonify({'message': 'logout successfully'}))
        response.set_cookie('auth', expires=0)
        return response
