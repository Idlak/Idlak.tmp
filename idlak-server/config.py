import os
import configparser
import uuid
import logging
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    JWT_SECRET_KEY = str(uuid.uuid4())


def load_config_file(conf):
    config = configparser.ConfigParser()
    config.read('config.ini')
    # JWT
    expiration_delta = config['JWT']['TOKEN_EXPIRATION_DELTA']
    conf['JWT_EXPIRATION_DELTA'] = timedelta(minutes=int(expiration_delta))
    # load all default
    for key in config['DEFAULT']:
        conf[key.upper()] = config['DEFAULT'][key]
    # set logging value
    if 'LOGGING' in conf:
        log = conf['LOGGING']
        if log == 'DEBUG':
            conf['LOGGING'] = logging.DEBUG
        elif log == 'INFO':
            conf['LOGGING'] = logging.INFO
        elif log == 'WARNING':
            conf['LOGGING'] = logging.WARNING
        elif log == 'ERROR':
            conf['LOGGING'] = logging.ERROR
        elif log == 'CRITICAL':
            conf['LOGGING'] = logging.CRITICAL
        else:
            conf['LOGGING'] = logging.NOTSET
    else:
        conf['LOGGING'] = logging.NOTSET
    return conf
