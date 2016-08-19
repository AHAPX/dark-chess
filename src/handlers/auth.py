import datetime
from urllib.parse import urljoin

from flask import request, make_response, Blueprint, abort

import config
from serializers import send_data, send_message, send_error, send_success
from decorators import authenticated, use_cache, login_required, validated
from models import User
from cache import delete_cache
from connections import send_mail_template, send_ws
from validators import RegistrationValidator, LoginValidator, ResetValidator, RecoverValidator
import errors


bp = Blueprint('auth', __name__, url_prefix='/v1/auth')


@bp.route('/register', methods=['POST'])
@validated(RegistrationValidator)
def register(data):
    username = data['username']
    password = data['password']
    email = data['email']
    user = User.add(username, password, email)
    if email:
        token = user.get_verification()
        data = {
            'username': username,
            'url': urljoin(config.SITE_URL, config.VERIFY_URL),
            'token': token,
        }
        send_mail_template('registration', [email], data=data)
    return send_message('registration successful')


@bp.route('/verification')
@authenticated
@login_required
def get_verification():
    try:
        token = request.user.get_verification()
    except Exception as exc:
        return send_error(exc.message)
    data = {
        'username': request.user.username,
        'url': urljoin(config.SITE_URL, config.VERIFY_URL),
        'token': token,
    }
    send_mail_template('verification', [request.user.email], data=data)
    return send_success()


@bp.route('/verification/<token>')
@use_cache(60)
def verify(token):
    user = User.get_by_token(token)
    if user:
        user.verify()
        delete_cache(token)
        return send_success()
    return send_error('token not found')


@bp.route('/reset', methods=['POST'])
@validated(ResetValidator)
def reset(data):
    try:
        user = User.get(User.email == data['email'])
    except User.DoesNotExist:
        return send_error('email not found')
    else:
        token = user.get_reset()
        data = {
            'username': user.username,
            'url': urljoin(config.SITE_URL, config.RECOVER_URL),
            'token': token,
        }
        send_mail_template('reset', [user.email], data=data)
    return send_success()


@bp.route('/recover/<token>', methods=['GET', 'POST'])
def recover(token):

    @validated(RecoverValidator)
    def _post(user, data):
        user.set_password(data['password'])
        user.save()
        delete_cache(token)
        return send_message('password changed')

    user = User.get_by_token(token)
    if user:
        if request.method == 'GET':
            return send_success()
        elif request.method == 'POST':
            return _post(user)
    return send_error('token not found')


@bp.route('/login', methods=['POST'])
@validated(LoginValidator)
def login(data):
    username = data['username']
    password = data['password']
    token = User.authenticate(username, password)
    if token:
        response = make_response(send_data({'auth': token}))
        expire_date = datetime.datetime.now() + datetime.timedelta(seconds=config.SESSION_TIME)
        response.set_cookie('auth', token, expires=expire_date)
        return response
    return send_error('username or password is incorrect')


@bp.route('/logout')
@authenticated
@login_required
def logout():
    delete_cache(request.auth)
    response = make_response(send_message('logout successfully'))
    response.set_cookie('auth', expires=0)
    return response


@bp.route('/authorized')
@authenticated
def authorized():
    if request.user:
        return send_data({'username': request.user.username})
    return send_error('not authorized')
