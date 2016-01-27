import datetime

from flask import request, make_response
from validate_email import validate_email

import config
from serializers import send_data, send_message, send_error, send_success
from decorators import authenticated
from models import User
from cache import delete_cache
from connections import send_mail_template
from app import app


@app.route('/auth/register', methods=['POST'])
def _register():
    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')
    if User.select().where(User.username == username).count():
        return send_error('username is already in use')
    if len(password) < 8:
        return send_error('password must be at least 8 characters')
    if email:
        if not validate_email(email):
            return send_error('email is not valid')
        if User.select().where(User.email == email).count():
            return send_error('email is already in use')
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
def _verify(token):
    if User.verify_email(token):
        return send_success()
    return send_error('token not found')


@app.route('/auth/login', methods=['POST'])
def _login():
    username = request.json.get('username')
    password = request.json.get('password')
    token = User.authenticate(username, password)
    if token:
        response = make_response(send_data({'auth': token}))
        expire_date = datetime.datetime.now() + datetime.timedelta(seconds=config.SESSION_TIME)
        response.set_cookie('auth', token, expires=expire_date)
        return response
    return send_error('username or password is incorrect')


@app.route('/auth/logout')
@authenticated
def _logout():
    delete_cache(request.auth)
    response = make_response(send_message('logout successfully'))
    response.set_cookie('auth', expires=0)
    return response
