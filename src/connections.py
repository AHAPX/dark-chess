import json

from flask import render_template
from redis import StrictRedis

import consts
from helpers import with_context


def check_email(email):
    if isinstance(email, str):
        return [email]
    elif isinstance(email, (list, tuple)):
        return email
    raise ValueError('invalid email')


def send_mail(recipients, subject, body, html=None, sender=None):
    from app import app

    msg = {
        'to': check_email(recipients),
        'subj': subject,
        'body': body,
    }
    if sender:
        msg['from'] = sender
    if html:
        msg['html'] = html

    redis = StrictRedis(
        app.config['SMTP_BROKER_HOST'],
        app.config['SMTP_BROKER_PORT'],
        app.config['SMTP_BROKER_DB']
    )
    redis.publish(app.config['SMTP_BROKER_CHANNEL'], json.dumps(msg))


def send_mail_template(name, recipients, data={}, sender=None):
    data = with_context(data)
    subject = render_template('email/{}_subj.plain'.format(name), **data)
    body_plain = render_template('email/{}_body.plain'.format(name), **data)
    body_html = render_template('email/{}_body.html'.format(name), **data)

    send_mail(recipients, subject, body_plain, body_html, sender)


def send_ws(message, signal=consts.WS_NONE, tags=[]):
    from app import app

    _tags = tags if isinstance(tags, list) else [tags]
    msg = {
        'message': {
            'message': message,
            'signal': signal,
            'tags': _tags,
        },
        'tags': _tags,
    }

    redis = StrictRedis(
        app.config['WS_BROKER_HOST'],
        app.config['WS_BROKER_PORT'],
        app.config['WS_BROKER_DB']
    )
    redis.publish(app.config['WS_BROKER_CHANNEL'], json.dumps(msg))
