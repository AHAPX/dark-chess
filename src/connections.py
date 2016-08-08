from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

from flask import render_template

import config
import consts
from helpers import with_context


def fill_msg(msg, subject, recipients, sender=None):
    msg['Subject'] = '{}{}'.format(config.MAIL_SUBJECT_PREFIX, subject)
    msg['From'] = sender or config.DEFAULT_MAIL_SENDER
    msg['To'] = recipients[0]
    if len(recipients) > 1:
        msg['Cc'] = recipients[1:]
    return msg


def send_mail(subject, body, recipients, sender=None):
    import tasks

    msg = fill_msg(MIMEText(body, 'text'), subject, recipients, sender)
    tasks.send_mail.delay(msg, recipients, sender)


def send_mail_template(name, recipients, sender=None, data={}):
    import tasks

    data = with_context(data)
    subject = render_template('email/{}_subj.plain'.format(name), **data)
    body_plain = render_template('email/{}_body.plain'.format(name), **data)
    body_html = render_template('email/{}_body.html'.format(name), **data)

    msg = fill_msg(MIMEMultipart('alternative'), subject, recipients, sender)
    msg.attach(MIMEText(body_plain, 'plain'))
    msg.attach(MIMEText(body_html, 'html'))
    tasks.send_mail.delay(msg, recipients, sender)


def send_ws(message, signal=consts.WS_NONE, tags=[]):
    import tasks

    msg = {
        'message': {
            'message': message,
            'signal': signal,
        },
        'tags': tags if isinstance(tags, list) else [tags],
    }
    tasks.send_ws.delay(json.dumps(msg))
