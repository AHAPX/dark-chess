from smtplib import SMTP, SMTP_SSL

from celery import Celery
from redis import StrictRedis

from app import app
import config


celery = Celery(__name__, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


@celery.task
def send_mail(msg, recipients, sender=None):
    sender = sender or config.DEFAULT_MAIL_SENDER
    if config.MAIL_USE_SSL:
        smtp_cls = SMTP_SSL
    else:
        smtp_cls = SMTP
    smtp = smtp_cls(host=config.MAIL_SERVER, port=config.MAIL_PORT)
    if config.MAIL_USE_TLS:
        smtp.ehlo()
        smtp.starttls()
    if config.MAIL_USERNAME:
        smtp.login(user=config.MAIL_USERNAME, password=config.MAIL_PASSWORD)
    smtp.sendmail(sender, recipients, msg.as_string())
    smtp.close()


@celery.task
def send_ws(msg):
    redis = StrictRedis(config.CACHE_HOST, config.CACHE_PORT, config.WS_DB)
    redis.publish(config.WS_CHANNEL, msg)
