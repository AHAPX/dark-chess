import logging


logger = logging.getLogger('base logger')


def getLogger(name, level=logging.INFO):
    log = logging.getLogger(name)
    log.setLevel(level)
    return log
