import os
from datetime import timedelta
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = 'super-secret'
    JWT_AUTH_USERNAME_KEY = 'uid'
    JWT_EXPIRATION_DELTA = timedelta(minutes=30)
