import datetime

from flask import request, make_response

import config
from serializers import send_data, send_message, send_error, send_success
from decorators import authenticated, use_cache, login_required
from models import User
from cache import delete_cache
from connections import send_mail_template
from app import app
from helpers import get_request_arg
from validators import RegistrationValidator, LoginValidator


@app.route('/auth/register', methods=['POST'])
def _register():
    username = get_request_arg(request, 'username')
    password = get_request_arg(request, 'password')
    email = get_request_arg(request, 'email')
    validator = RegistrationValidator(username, password, email)
    if not validator.is_valid():
        return send_error(validator.get_error())
    user = User.add(username, password, email)
    if email:
        token = user.get_verification()
        data = {
            'username': username,
            'token': token,
        }
        send_mail_template('registration', [email], data=data)
    return send_message('registration successful')


@app.route('/auth/verification/')
@authenticated
@login_required
def _get_verification():
    try:
        token = request.user.get_verification()
    except Exception as exc:
        return send_error(exc.message)
    data = {
        'username': request.user.username,
        'token': token,
    }
    send_mail_template('verification', [request.user.email], data=data)
    return send_success()


@app.route('/auth/verification/<token>')
@use_cache(60)
def _verify(token):
    if User.verify_email(token):
        return send_success()
    return send_error('token not found')


@app.route('/auth/login', methods=['POST'])
def _login():
    username = get_request_arg(request, 'username')
    password = get_request_arg(request, 'password')
    validator = LoginValidator(username, password)
    if validator.is_valid():
        token = User.authenticate(username, password)
        if token:
            response = make_response(send_data({'auth': token}))
            expire_date = datetime.datetime.now() + datetime.timedelta(seconds=config.SESSION_TIME)
            response.set_cookie('auth', token, expires=expire_date)
            return response
    return send_error(validator.get_error())


@app.route('/auth/logout')
@authenticated
@login_required
def _logout():
    delete_cache(request.auth)
    response = make_response(send_message('logout successfully'))
    response.set_cookie('auth', expires=0)
    return response
